from lib2to3.pgen2 import token
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.conf import settings
import datetime
from .models import Cuisine ,CustomAdmin,ObjCount,cart
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.mail import send_mail , EmailMessage
from django.views.generic import View
from menumaker.utils import render_to_pdf , render_to_mypdf
from . import forms
from tablib import Dataset
from django.contrib import messages
from .resources import CuisineResource

# Create your views here.	

def send_verification_email(email, token):
    message = "<a href=http://127.0.0.1:8000/user/verify-user/{email}/{token}/>Click here to verify your email</a>".format(email=user_email,token = token)



    subject = "Verify your email id"
    email = EmailMessage(subject , message ,settings.EMAIL_HOST_USER,[email])
    email.content_subtype = 'html'

    send = email.send()
    if send:
        return True
    else :
        return False		


def signup(request):
    if request.method == 'POST':
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        username = request.POST['username']
        match_user = User.objects.all().filter(username = username).count()
        match_email = User.objects.all().filter(email = email).count()  #<QuerySet [<User: amangupta1542@gmail.com>, <User: ram>, <User: rajgupta851>, <User: >]>
		# on filter(username = username) got this <QuerySet [<User: rajgupta851>]>
        passwd = request.POST['password']
        cpasswd = request.POST['cpass']
        if passwd == cpasswd:
            if match_user:
                messages.info(request , 'Username already exist' , extra_tags='exist')
            if match_email:
                messages.info(request , 'Email already registered' , extra_tags='exist')
            else:
                u = User(first_name=fname,last_name=lname,email=email,password=make_password(passwd),username=username)
                send_verification_email(email, token)
                u.save()
                messages.info(request , 'You registered Successfully' , extra_tags='registered')
                return redirect('/login/')
				# return HttpResponseRedirect('/profiles/'+in_username)
        else:
            messages.info(request , 'Passwords should be same' , extra_tags='notmatch')
    return render(request, 'menumakerapp/signup.html')


def login_call(request):
	if request.method == 'POST':
		uname = request.POST['username']
		passwd = request.POST['password']
		currentUser = authenticate(username=uname, password=passwd)
		admin = CustomAdmin.objects.filter(username=uname, password = passwd).count()
		if currentUser:
			login(request, currentUser)
			uObj = User.objects.get(username=request.user)
			return redirect('/')
		elif admin == 1:
			request.session['name'] = uname
			# return render(request , 'menumakerapp/admin_page.html',{'user': user , 'passw':passw})
			return redirect('/')
		else:
			messages.info(request, 'Username and password not match' ,extra_tags='notmatch')
			# return redirect('/signup/')
	return render(request, 'menumakerapp/login.html')

def logout_call(request):
	logout(request)
	return redirect('/login/')


###### find biggest item ########
def findBig(request):
	uObj = User.objects.get(username=request.user)
	c = cart.objects.all().filter(user=uObj)
	obj_count = c.count()
	obj_list = []
	usr_obj = ObjCount.objects.filter(objuser=uObj)
	count_obj = usr_obj.count()
	print(count_obj)
	if count_obj :
		compare_list =[]
		remain_item = []
		remain_item_list = []
		for a in range(0 , count_obj):
			oa_list = usr_obj[a].objlist
			split_oalist = oa_list[1:-1].split(",")
			## ERROR IN split_str_list
			l_obj = int(split_oalist[-1]) #taking last from list
			compare_list.append(l_obj)
			max_num = max(compare_list)

		totle_user_obj = c[0:obj_count]
		for i in totle_user_obj:
			if i.id > max_num:
				remain_item = cart.objects.filter(id = i.id)[0]
				remain_item_list.append(remain_item)

		if remain_item:
			remain_count = len(remain_item_list)
		for it in remain_item_list:
			if it not in obj_list:
				obj_list.append(it.id)
		return obj_list
	else:
		for oc in c:
			if oc not in obj_list:
				obj_list.append(oc.id)
		return obj_list

###### end find ########
def cartadd(request, id,role):
	if request.user.is_active:
		listobj = findBig(request)
		paid = False
		uf = request.user.first_name[:1]
		ul = request.user.last_name[:1]
		back = request.GET.get('back')
		cuisine_list = Cuisine.objects.only("cuisine").filter(role = role)
		c_list = []
		for cui in cuisine_list :
			if cui.cuisine not in c_list:
				c_list.append(cui.cuisine)
		c_list.sort();
		exist = True
		vObj = Cuisine.objects.get(id=id)
		#print(vObj.id)
		#####if item priviously added
		if listobj :
			for i in listobj:
				cid = cart.objects.filter(id = i)
				if cid[0].items.id == vObj.id:
					exist = False
					messages.info(request,'Item already added to the list', extra_tags='already')
		cu = vObj.cuisine 
		if exist:
			uObj = User.objects.get(username=request.user)
			cobj = ObjCount.objects.filter(objuser=uObj)
			if cobj.count() <= 4:
				c = cart(user=uObj, items=vObj)
				c.save()
				messages.info(request, 'Successfully added to the cart' ,extra_tags= 'added')
			else:
				if not paid:
					messages.info(request, 'Your not paid user' ,extra_tags= 'notpaidusr')
				else:
					c = cart(user=uObj, items=vObj)
					c.save()
					messages.info(request, 'Successfully added to the cart' ,extra_tags= 'added')
		if back:
			return render(request, 'menumakerapp/list_cuisines.html', {'role':role , 'cuisine':c_list,'first':uf,'last':ul})
		else:
			lObj = Cuisine.objects.all().filter(cuisine=cu , role=role)
			return render(request, 'menumakerapp/list_menu.html', {'data':lObj,'role':role , 'cuisine':c_list,'first':uf,'last':ul})
	else:
		return redirect('/login/')

def welcome(request):
	if 'name' in request.session:
		total_menu_yet = ObjCount.objects.all().count()
		# print('index page for admin welcome view')
		# print(total_menu_yet)
		admin=request.session['name']
		user_count= User.objects.all().count()
		cuisine_count = Cuisine.objects.all().count()
		return render(request , 'menumakerapp/index.html',{'admin':admin,'user_count':user_count , 'cuisine_count':cuisine_count, 'total_menu_yet':total_menu_yet})
	else:
		if request.user.is_authenticated:
			uf = request.user.first_name[:1]
			ul = request.user.last_name[:1]
			return render(request , 'menumakerapp/index.html' , {'first':uf,'last':ul})
		else:
			return render(request , 'menumakerapp/index.html')


def list_cuisines(request):
	######### interacte with Cuisine model
	iObj = request.GET.get('cuisine')
	rObj = request.GET.get('role')
	back = False
	if 'back' in request.GET:
		back = request.GET['back']
	#print(back)
	if back:
		cuisine_list = Cuisine.objects.only("cuisine").filter(role = back)
	else:
		cuisine_list = Cuisine.objects.only("cuisine").filter(role = rObj)
	c_list = []
	for cui in cuisine_list :
		if cui.cuisine not in c_list:
			c_list.append(cui.cuisine)
	c_list.sort();
	if request.user.is_authenticated:
		uf = request.user.first_name[:1]
		ul = request.user.last_name[:1]
		if iObj:
	#		vObj = Cuisine.objects.filter(cuisine=iObj, role=rObj)
			vObj = Cuisine.objects.all().filter(cuisine=iObj.title() , role=rObj)
			return render(request, 'menumakerapp/list_menu.html', {'data':vObj,'cuiObj':iObj,'role':rObj,'first':uf,'last':ul})
		if back:
			return render(request, 'menumakerapp/list_cuisines.html', {'role':back ,'cuisine':c_list,'first':uf,'last':ul})
		return render(request, 'menumakerapp/list_cuisines.html', {'role':rObj ,'cuisine':c_list,'first':uf,'last':ul})
	else :
		print('okk')
		if iObj:
	#		vObj = Cuisine.objects.filter(cuisine=iObj, role=rObj)
			vObj = Cuisine.objects.all().filter(cuisine=iObj.title() , role=rObj)
			return render(request, 'menumakerapp/list_menu.html', {'data':vObj,'cuiObj':iObj,'role':rObj,})
		if back:
			return render(request, 'menumakerapp/list_cuisines.html', {'role':back ,'cuisine':c_list})
	return render(request, 'menumakerapp/list_cuisines.html', {'role':rObj ,'cuisine':c_list})


# coding for selected cuisine

def my_page(request):
	x= datetime.datetime.now()
	date = x.strftime("%d")
	month = x.strftime("%m")
	year = x.strftime("%y")
	paidUser = False

	if request.user.is_authenticated:
		uf = request.user.first_name[:1]
		ul = request.user.last_name[:1]

	user_req_for = request.GET.get('cui')

	user_req_last = request.GET.get('last_cui')
	#print(user_req_for)
	#next line work correctly
	uObj = User.objects.get(username=request.user)
	usr_obj = ObjCount.objects.filter(objuser=uObj)
	print(usr_obj)
	obj_creation_date = []
	for cre_date in usr_obj:
		obj_creation_date.append(cre_date.createDate)
	count_obj = usr_obj.count()
	print(obj_creation_date)
	for d in obj_creation_date:
		print(d)
	#print(count_obj)
	#now selection of this user objects from cart
	c = cart.objects.all().filter(user=uObj)
	obj_count = c.count()
	obj_list = []
	# print(obj_count)
	# print(uObj)
	cdate = date+"/"+month+"/"+year
	### print(cdate) 26/03/21
	### print(type(cdate)) <class 'str'>
	# User at first time
	if count_obj<1:

		for oc in c:
			if oc not in obj_list:
				obj_list.append(oc.id)
		if request.POST.get("save-btn"):
			ob = ObjCount(objuser=uObj,createDate=cdate,objcount=obj_count,objlist=obj_list)
			ob.save()
			count_obj = ObjCount.objects.filter(objuser=uObj).count()
			# print(count_obj)
			return render(request,'menumakerapp/my_page.html',{'count_obj':range(count_obj),'date':cdate,'creat_date':obj_creation_date})

		breakfast = []
		lunch = []
		dinner = []
		hightea = []
		brunch = []
		save = False
		for i in c :
			save = True
			if i.items.role == 'Breakfast':
				breakfast.append(i)
			if i.items.role == 'Lunch':
				lunch.append(i)
			if i.items.role == 'Dinner':
				dinner.append(i)
			if i.items.role == 'Hightea':
				hightea.append(i)
			if i.items.role == 'Brunch':
				brunch.append(i)

		#return render(request,'menumakerapp/my_page.html',{'data':uObj})
		b_count = 0 #breakfast count
		l_count = 0 #lunch count
		d_count = 0# dinner count
		h_count = 0#hightea count
		br_count = 0#brunch count
		for i in c:
			#print(i.items.role)
			if i.items.role == 'Breakfast' :
				b_count = b_count+1
			elif i.items.role == 'Lunch' :
				l_count = l_count+1
			elif i.items.role == 'Dinner' :
				d_count = d_count+1
			elif i.items.role == 'Hightea' :
				h_count = h_count+1
			elif i.items.role == 'Brunch' :
				br_count = br_count+1
			else:
				pass
		my_dict = {
		'save':save ,
		'data' : c ,
		'user' : uObj ,
		'b_count' : b_count ,
		'l_count' : l_count ,
		'd_count' : d_count ,
		'h_count' : h_count ,
		'br_count' :br_count ,
		'breakfast':breakfast,
		'lunch':lunch,
		'dinner':dinner,
		'hightea':hightea,
		'brunch':brunch,
		'date':cdate,
		'count_obj': 'f',
		'first':uf,
		'last':ul
		}
		return render(request,'menumakerapp/my_page.html',context = my_dict)
	else:
		if user_req_for:
			z_value = int(user_req_for) - 1
		else :
			z_value = 0

		###### if z-value is greate then 0 to ek variable set karengy jis se yadi user date pr click karega to forloop counter band ho jayga for bs cuisine dikhega
		run_forloop = True
		if not request.POST.get("save-btn"):
			if user_req_for or user_req_last :
				run_forloop=False

		try:
			usr_obj[z_value]

		except IndexError:
			return render(request,'menumakerapp/menu_not_available.html',{'id':user_req_for})

		##### end section #######
		o_list = usr_obj[z_value].objlist
		# print(o_list)
		o_date = usr_obj[z_value].createDate
		# print(o_date)
		#print(type(eval(o_list)))
		#print(type(o_list[1:-1].split(",")))
		split_str_list = o_list[1:-1].split(",")

		converted_list= []
		for z in split_str_list:
			converted_list.append(int(z))


		compare_list =[]
		remain_item = []
		remain_item_list = []
		objsum = 0

		############# for last and biggest object ##########
		for a in range(0 , count_obj):
			oa_list = usr_obj[a].objlist
			split_oalist = oa_list[1:-1].split(",")
			# print(split_oalist)
			# print(len(split_oalist))
			objsum = objsum + len(split_oalist)
			l_obj = int(split_oalist[-1])
			compare_list.append(l_obj)
			max_num = max(compare_list)
		#print(max_num)
		totle_user_obj = c[0:obj_count]
		for i in totle_user_obj:
			if i.id > max_num:
				remain_item = cart.objects.filter(id = i.id)[0]
				remain_item_list.append(remain_item)

		if remain_item:
			remain_count = len(remain_item_list)
			# cdate = o_date
		for it in remain_item_list:
			if it not in obj_list:
				obj_list.append(it.id)

		# print(obj_list)
		############# end last object ##############
		if request.POST.get("save-btn"):
			match = True
			uo = ObjCount.objects.filter(objuser = uObj)
			print(uo)
			obj_count = obj_count-objsum
			if len(obj_list) != 0:

				for u in uo :
					if obj_list==u.objlist:
						match = False
				if match:
					if count_obj <= 4:
						ob = ObjCount(objuser=uObj,createDate=cdate,objcount=obj_count,objlist=obj_list)
						ob.save()
					else :
						if not paidUser:
							messages.info(request, 'Your not paid user' ,extra_tags= 'notpaid')
						else :
							#remain_item = True
							ob = ObjCount(objuser=uObj,createDate=cdate,objcount=obj_count,objlist=obj_list)
							ob.save()
			# count_obj = ObjCount.objects.filter(objuser=uObj).count()
			count_obj = len(obj_creation_date)
			# print(count_obj)
			return render(request,'menumakerapp/my_page.html',{'count_obj':range(count_obj),'date':cdate,'creat_date' :obj_creation_date ,'first':uf,'last':ul,'run_forloop':run_forloop})


		breakfast = []
		lunch = []
		dinner = []
		hightea = []
		brunch = []
		save = False
		if user_req_last:
			save = True
			for i in remain_item_list :
				if i.items.role == 'Breakfast':
					breakfast.append(i)
				if i.items.role == 'Lunch':
					lunch.append(i)
				if i.items.role == 'Dinner':
					dinner.append(i)
				if i.items.role == 'Hightea':
					hightea.append(i)
				if i.items.role == 'Brunch':
					brunch.append(i)

		else:
			for i in converted_list :
				#print(cart.objects.all().filter(id = i))
				j = cart.objects.all().filter(id = i)[0].items.role
				if j == 'Breakfast':
					breakfast.append(cart.objects.all().filter(id = i)[0])
				elif j == 'Lunch':
					lunch.append(cart.objects.all().filter(id = i)[0])
				elif j == 'Dinner':
					dinner.append(cart.objects.all().filter(id = i)[0])
				elif j == 'Hightea':
					hightea.append(cart.objects.all().filter(id = i)[0])
				elif j == 'Brunch':
					brunch.append(cart.objects.all().filter(id = i)[0])
				else:
					pass

		b_count = 0 #breakfast count
		l_count = 0 #lunch count
		d_count = 0# dinner count
		h_count = 0#hightea count
		br_count = 0#brunch count
		for i in c:
			#print(i.items.role)
			if i.items.role == 'Breakfast' :
				b_count = b_count+1
			elif i.items.role == 'Lunch' :
				l_count = l_count+1
			elif i.items.role == 'Dinner' :
				d_count = d_count+1
			elif i.items.role == 'Hightea' :
				h_count = h_count+1
			elif i.items.role == 'Brunch' :
				br_count = br_count+1
			else:
				pass
		my_dict = {
		'save': save,
		'data' : user_req_for or user_req_last ,
		'user' : uObj ,
		'b_count' : b_count ,
		'l_count' : l_count ,
		'd_count' : d_count ,
		'h_count' : h_count ,
		'br_count' :br_count ,
		'breakfast':breakfast,
		'lunch':lunch,
		'dinner':dinner,
		'hightea':hightea,
		'brunch':brunch,
		'date':usr_obj[z_value].createDate,
		'id':z_value+1,
		'creat_date' :obj_creation_date,
		'count_obj':range(count_obj),
		'remain_item':remain_item,
		'first':uf,
		'last':ul,
		'run_forloop':run_forloop
		}
		return render(request,'menumakerapp/my_page.html',context = my_dict)


class GeneratePdf(View):
	def get(self , request , *args, **kwargs):
		x= datetime.datetime.now()
		date = x.strftime("%d")
		month = x.strftime("%m")
		year = x.strftime("%y")
		uObj = User.objects.get(username = request.user)
		c = cart.objects.all().filter(user=uObj)

		id = int(request.GET.get('id'))
		id = id-1
		usr_obj = ObjCount.objects.filter(objuser=uObj)
		# print(usr_obj)
		count_obj = usr_obj.count()
		o_list = usr_obj[id].objlist

		o_date = usr_obj[id].createDate
		# print(o_date)
		# print(o_list)
		# print(o_list)
		split_str_list = o_list[1:-1].split(",")

		converted_list= []
		for z in split_str_list:
			converted_list.append(int(z))
		# print(converted_list)
		# print(id)
		# print(type(id))
		# print(usr_obj[id])

		breakfast = []
		lunch = []
		dinner = []
		hightea = []
		brunch = []
		for i in converted_list :
			# print('okk')
			# print(cart.objects.all().filter(id = i))
			# print('okk')
			j = cart.objects.all().filter(id = i)[0].items.role
			if j == 'Breakfast':
				breakfast.append(cart.objects.all().filter(id = i)[0])
			elif j == 'Lunch':
				lunch.append(cart.objects.all().filter(id = i)[0])
			elif j == 'Dinner':
				dinner.append(cart.objects.all().filter(id = i)[0])
			elif j == 'Hightea':
				hightea.append(cart.objects.all().filter(id = i)[0])
			elif j == 'Brunch':
				brunch.append(cart.objects.all().filter(id = i)[0])
			else:
				pass
		pdf = render_to_pdf('menumakerapp/my_page.html',{'count_obj':count_obj,'data':c,'user':uObj,'breakfast':breakfast,'lunch':lunch,'dinner':dinner,'hightea':hightea,'brunch':brunch,'date':o_date})
		return HttpResponse(pdf , content_type='application/pdf')

###directly download GeneratePdf
class DownloadPdf(View):
	def get(self , request , *args , **kwargs ):
		x= datetime.datetime.now()
		date = x.strftime("%d")
		month = x.strftime("%m")
		year = x.strftime("%y")
		uObj = User.objects.get(username = request.user)
		c = cart.objects.all().filter(user=uObj)

		id = int(request.GET.get('id'))
		id = id-1
		usr_obj = ObjCount.objects.filter(objuser=uObj)
		# print(usr_obj)
		count_obj = usr_obj.count()
		o_list = usr_obj[id].objlist

		o_date = usr_obj[id].createDate
		# print(o_list)
		# print(o_list)
		split_str_list = o_list[1:-1].split(",")

		converted_list= []
		for z in split_str_list:
			converted_list.append(int(z))
		# print(converted_list)
		# print(id)
		# print(type(id))
		# print(usr_obj[id])

		breakfast = []
		lunch = []
		dinner = []
		hightea = []
		brunch = []
		for i in converted_list :
			# print('okk')
			# print(cart.objects.all().filter(id = i))
			# print('okk')
			j = cart.objects.all().filter(id = i)[0].items.role
			if j == 'Breakfast':
				breakfast.append(cart.objects.all().filter(id = i)[0])
			elif j == 'Lunch':
				lunch.append(cart.objects.all().filter(id = i)[0])
			elif j == 'Dinner':
				dinner.append(cart.objects.all().filter(id = i)[0])
			elif j == 'Hightea':
				hightea.append(cart.objects.all().filter(id = i)[0])
			elif j == 'Brunch':
				brunch.append(cart.objects.all().filter(id = i)[0])
			else:
				pass
		pdf = render_to_pdf('menumakerapp/my_page.html',{'count_obj':count_obj,'data':c,'user':uObj,'breakfast':breakfast,'lunch':lunch,'dinner':dinner,'hightea':hightea,'brunch':brunch,'date':o_date})
		response = HttpResponse(pdf, content_type='application/pdf')
		filename = "Cuisine.pdf"
		content = "attachment; filename = %s" %(filename)
		response['Content-Disposition'] = content
		return response



def send_email(request):
	x= datetime.datetime.now()
	date = x.strftime("%d")
	month = x.strftime("%m")
	year = x.strftime("%y")
	uObj = User.objects.get(username = request.user)
	c = cart.objects.all().filter(user=uObj)

	id = request.POST.get('cuisine_id')
	id = int(id)
	id = id-1
	usr_obj = ObjCount.objects.filter(objuser=uObj)
	# print(usr_obj)
	count_obj = usr_obj.count()
	o_list = usr_obj[id].objlist

	o_date = usr_obj[id].createDate
	# print(o_list)
	# print(o_list)
	split_str_list = o_list[1:-1].split(",")

	converted_list= []
	for z in split_str_list:
		converted_list.append(int(z))

	breakfast = []
	lunch = []
	dinner = []
	hightea = []
	brunch = []
	for i in converted_list :
		# print('okk')
		# print(cart.objects.all().filter(id = i))
		# print('okk')
		j = cart.objects.all().filter(id = i)[0].items.role
		if j == 'Breakfast':
			breakfast.append(cart.objects.all().filter(id = i)[0])
		elif j == 'Lunch':
			lunch.append(cart.objects.all().filter(id = i)[0])
		elif j == 'Dinner':
			dinner.append(cart.objects.all().filter(id = i)[0])
		elif j == 'Hightea':
			hightea.append(cart.objects.all().filter(id = i)[0])
		elif j == 'Brunch':
			brunch.append(cart.objects.all().filter(id = i)[0])
		else:
			pass
	pdf = render_to_mypdf('menumakerapp/my_page.html',{'count_obj':count_obj,'data':c,'user':uObj,'breakfast':breakfast,'lunch':lunch,'dinner':dinner,'hightea':hightea,'brunch':brunch,'date':o_date})

	message = request.POST.get('message','')
	subject = request.POST.get('subject','')
	mail_id = request.POST.get('email','')
	email = EmailMessage(subject , message ,settings.EMAIL_HOST_USER,[mail_id])
	email.content_subtype = 'html'

	email.attach("Cuisine.pdf",pdf,'application/pdf')
	email.send()
	return redirect('/')


def cadmin(request):
	if 'name' not in request.session:
		form = forms.CustomAdminForm()
		if request.method == 'POST':
			form = forms.CustomAdminForm(request.POST)
			if form.is_valid():
				user = form.cleaned_data['username']
				passw = form.cleaned_data['password']
				usr = CustomAdmin.objects.filter(username=user, password = passw).count()
				if usr == 1:
					request.session['name'] = user
					# return render(request , 'menumakerapp/admin_page.html',{'user':user , 'passw':passw})
					return redirect('/admin_page/')
		return render(request ,'menumakerapp/custom_admin.html', {'form':form})
	else:
		return redirect('/admin_page/')
def admin_page(request):
	if 'name' in request.session:
		admin=request.session['name']
		return render(request , 'menumakerapp/admin_page.html' ,{'admin':admin})
	else:
		return redirect('/cadmin/')

def logout_admin(request):
	logout(request)
	# del request.session['name']
	# return redirect('/cadmin/')
	return redirect('/login/')


def users_list(request):
	if 'name' in request.session:
		admin=request.session['name']
		user_list = User.objects.all()  #<QuerySet [<User: amangupta1542@gmail.com>, <User: ram>, <User: rajgupta851>]>
		####### taking total times of a user #######
		u_count = {}
		usr_c = ObjCount.objects.all()
		##print(usr_c)
		for i in usr_c:
			if i.objuser not in u_count :
				#print(i.objuser) ## username
				countu = ObjCount.objects.filter(objuser = i.objuser).count()
				##print(countu) #1
				u_count[i.objuser] = countu
		##print(u_count) #working
		####### end taking total times of a user #######
		return render(request,'menumakerapp/users_list.html',{'user_list':user_list,'admin':admin , 'u_count':u_count})
	else:
		return redirect('/cadmin/')

def bulk(request):
	return HttpResponse(request , 'menumakerapp/add_cuisine')

def add_cuisine(request):
	if 'name' in request.session:
		cuisine_list = Cuisine.objects.only("cuisine");
		cuisine_type = Cuisine.objects.only("role");
		c_type = []
		c_list = []
		for cui in cuisine_list :
			if cui.cuisine not in c_list:
				c_list.append(cui.cuisine)
		if 'newCuisine' in request.GET:
			newCuisine = request.GET['newCuisine']
			toT = newCuisine.title()
			if toT not in c_list:
				c_list.append(toT)

		c_list.sort();
		for t in cuisine_type :
			if t.role not in c_type:
				c_type.append(t.role)
		c_type.sort();
		admin=request.session['name']

		####### bulk upload ########
		if request.method == 'POST' :
		# if 'CuisineFile' in request.POST:
			cuisine_resource = CuisineResource()
			dataset = Dataset()
			#if 'CuisineFile' in request.POST:
			new_cui = request.FILES['CuisineFile']
			#else:
				#return HttpResponse('Something went wrong')

			if not new_cui.name.endswith('xlsx'):
				messages.info(request , 'Wrong format data only .xlsx format is accepted' , extra_tags='err')
				return render(request,'menumakerapp/add_cuisine.html',{'admin':admin , 'cuisine':c_list , 'type':c_type})
			else:
				imported_data=dataset.load(new_cui.read(),format = 'xlsx')
				for data in imported_data:
					value = Cuisine(
						data[0],
						data[1],
						data[2],
						data[3]
						)
					value.save()
				messages.success(request, 'Upload Successfully' , extra_tags='success')
				return redirect('/bulk/')
				#return render(request,'menumakerapp/add_cuisine.html',{'admin':admin , 'cuisine':c_list , 'type':c_type})
		####### bulk upload end ########
		return render(request,'menumakerapp/add_cuisine.html',{'admin':admin , 'cuisine':c_list , 'type':c_type})
	else:
		return redirect('/cadmin/')

def add_cuisine_data(request):
	# newCuisine = request.GET['aman']
	cuisine = request.GET['cuisine']
	type = request.GET['type']
	item = request.GET['item']
	#####Checking of item existance prebiously ######
	item_ex = Cuisine.objects.only(item).filter(cuisine=cuisine, item=item, role=type).count()
	print(item_ex)
	###### end checking#########
	if not item_ex:
		c = Cuisine(cuisine=cuisine , item=item , role=type)
		c.save()
	else:
		messages.info(request,'Item is exist' , extra_tags='item_ex')
	return redirect('/add_cuisine/')

def add_admin(request):
	if 'name' in request.session:
		admin=request.session['name']
		form = forms.CustomAdminForm()
		if request.method == 'POST':
			form = forms.CustomAdminForm(request.POST)
			if form.is_valid():
				u = form.cleaned_data['username']
				upass = form.cleaned_data['password']
				cpass = form.cleaned_data['cpassword']
				if upass == cpass:
					exist = CustomAdmin.objects.all().filter(username = u)
					if exist:
						messages.info(request , 'Admin already exist' , extra_tags = 'exist')
					else:
						if form.is_valid():
							form.save(commit=True)
							messages.info(request , 'Admin add Successfully' , extra_tags='add')
				else:
					messages.info(request , 'Passwords should be same' , extra_tags='notmatch')
		return render(request,'menumakerapp/add_admin.html', {'form':form ,'admin':admin})
	else:
		return redirect('/cadmin/')


def all_cuisine_list(request):
	if 'name' in request.session:
		admin=request.session['name']
		cuisine_list = Cuisine.objects.all()
		btn = request.GET.get('role')
		id = request.GET.get('id')
		if id:
			id=int(id)
		idexist = Cuisine.objects.filter(id = id).exists()
		editC = False
		# if 'savebtn' in request.GET:
		# 	print('okk')
		c_id = request.GET.get('id')
		cuisine = request.GET.get('cuisine')
		item = request.GET.get('item')
		role = request.GET.get('role')
		if 'savebtn' in request.GET:
			id = False
			cui_obj = Cuisine.objects.filter(id = c_id ).update(cuisine = cuisine , item = item , role = role)
			# cui_obj.cuisine = cuisine
			# cui_obj.item = item
			# cui_obj.role = role
			# cui_obj.save()

		if idexist:
			if btn=='edit':
				editC = True
			elif btn=='delete':
				Cuisine.objects.filter(id = id).delete()
			else:
				pass
		return render(request , 'menumakerapp/all_cuisine_list.html' ,{'cuisine_list':cuisine_list,'admin':admin,'edit':editC , 'editid':id})
	else:
		return redirect('/cadmin/')


def profile(request):
	uObj = User.objects.get(username=request.user)
	if request.user.is_authenticated:
		uf = request.user.first_name[:1]
		ul = request.user.last_name[:1]
	#now selection of this user objects from cart
	c = cart.objects.all().filter(user=uObj).count()
	if c == 0:
		return render(request , 'menumakerapp/user_profile.html', {'first':uf,'last':ul})
	else:
		return redirect('/my_page/')








def send_verification_email(user_email , token):
    message = "<a href='http://127.0.0.1:8000/user/verify-user/{email}/{token}/'>Click here to verify your email</a>".format(email=user_email,token = token)



    subject = "Verify your email id"
    email = EmailMessage(subject , message ,settings.EMAIL_HOST_USER,[user_email])
    email.content_subtype = 'html'

    send = email.send()
    if send:
        return True
    else :
        return False		
