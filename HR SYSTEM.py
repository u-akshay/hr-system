from flask import Flask,render_template,request,session,redirect,url_for
from DBConnection import Db

from werkzeug.utils import secure_filename
import os
import time

import PyPDF2


db = Db()

app = Flask(__name__)
app.secret_key="asd"


APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/photos')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

UPLOAD_FOLDER1 = os.path.join(APP_ROOT, 'static/resume')
ALLOWED_EXTENSIONS1 = {'pdf'}
app.config['UPLOAD_FOLDER1'] = UPLOAD_FOLDER1


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_pdffile(filename):
    return '.' in filename and filename.rsplit('.', 1) [1].lower() in ALLOWED_EXTENSIONS1


#########################################################


############################################################################# LOGIN

@app.route('/')
def login():
    return render_template('index.html')

@app.route('/login_pst',methods=['POST'])
def login_pst():
    username=request.form["username"]
    password=request.form["password"]
    qry=db.selectOne("SELECT * FROM login WHERE userName='"+username+"' AND password='"+password+"' ")
    if qry is not None:
        if qry["type"]=="Admin":
            return ''' <script> alert('login success');window.location="/admin_profile"; </script> '''

        elif(qry["type"]=="Candidate"):
            q=db.selectOne("SELECT * FROM candidate_signup WHERE candidate_signup.loginID='"+str(qry["id"])+"'")
            if q is not None:
                session["userid"]=q["userID"]
                return ''' <script>alert('login success');window.location="/candidate_profile"; </script> '''
            else:
                return ''' <script>alert('Invalid Username or Password');window.location="/"; </script> '''

        elif (qry["type"] == "Company"):
            q = db.selectOne("SELECT * FROM company WHERE company.loginID='" + str(qry["id"]) + "'")
            if q is not None:
                session["userid"] = q["Id"]
                return ''' <script>alert('login success');window.location="/company_profile"; </script> '''
            else:
                return ''' <script>alert('Invalid Username or Password');window.location="/"; </script> '''

        elif qry["type"]=="pending":
            return ''' <script> alert('please wait for admin aproval');window.location="/"; </script> '''

        elif qry["type"] == "rejected":
            return ''' <script> alert('This account is rejected');window.location="/"; </script> '''


    else:
        return ''' <script>alert('Invalid Username or Password');window.location="/"; </script> '''


#############################################################################################


############################################################################### COMPANY MODULE


@app.route('/company_profile')
def comapnyProfile():
    return render_template('company profile.html')

@app.route('/company_profile_edit')
def companyEdit():

    res = db.selectOne("SELECT * from company where Id = '"+ str(session['userid']) +"' ")

    return render_template('Company Profile Management.html', data = res)

@app.route('/update_company',methods=['POST'])
def update_company():
    Name=request.form['Name']
    Place=request.form['Place']
    Post=request.form['Post']
    pin=request.form['pin']
    email=request.form['email']
    website=request.form['website']
    phone=request.form['phone']

    qry="update company set name = '"+Name+"' ,place = '"+Place+"', post = '"+Post+"', pin = '"+pin+"', email = '"+email+"', website = '"+website+"', phone = '"+phone+"' where Id='"+str(session['userid'])+"' "
    db.update(qry)
    return '''<script>alert('Updated' ); window.location='/company_profile_edit'; </script> '''



@app.route('/edit_company_photo')
def edit_company_photo():
    return render_template('Edit_Company_Photo.html')


@app.route('/update_company_photo', methods=['POST'])
def update_company_photo():

    picture = request.files['fileField']

    if picture and allowed_file(picture.filename):

        timestr = time.strftime("%Y%m%d-%H%M%S")
        filename = timestr+secure_filename(picture.filename)
        picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        db.update("update company set photo = '"+filename+"' where Id = '"+str(session['userid'])+"' ")
        return redirect('/company_profile_edit')

    else:
        return '''<script>alert('File Not Supported' ); window.location='/company_profile_edit'; </script> '''

@app.route('/vacancy_add')
def vacancyAdd():

    res = db.select("select * from skills")

    return render_template('vacancy add.html', data = res)

@app.route('/vaccancyAdd_post', methods=['POST'])
def vaccancyAdd_post():
    vacancy_name=request.form['vacancy_name']
    number_of_vacancy=request.form['number_of_vacancy']
    description=request.form['description']

    skill_ids =request.form.getlist('checkbox')
    skill = ""
    for id in skill_ids:
        skill = skill+id+","

    qry = "insert into vacancyadd VALUES(NULL,'" + vacancy_name + "','" + number_of_vacancy + "','" + description + "','" + str(session['userid']) + "', '"+skill+"','open',now())"
    db.insert(qry)
    return '''<script>alert('Job Details Added' ); window.location='/vacancy_add'; </script> '''


#####################################################################################

#################################################################################### CANDIDATE MODULE


@app.route('/candidate_profile')
def candidateProfile():
    return render_template('candidate profile.html')


@app.route('/job_vacancy')
def job_vacancy():
    res = db.select("SELECT * FROM `vacancyadd` WHERE `companyID`='" + str(session['userid']) + "' ORDER BY `ID` DESC ")

    return render_template('company view vaccancy.html', data=res)

@app.route('/job_vacancy_can/<id>')
def job_vacancy_can(id):
    # res = db.select("SELECT `applytable`.*,`candidate_signup`.* FROM `candidate_signup`,`applytable` WHERE `applytable`.`vacancyid`='"+id+"' AND `candidate`=`candidate_signup`.`userID`")
    import collections
    db1 = Db()
    res = db1.selectOne("SELECT * FROM `vacancyadd` WHERE `ID`='"+id+"'")
    lis = []
    new=[]

    if res is not None:
        vskills = res['skill']
        vskills = vskills[:-1]
        vskill = vskills.split(',')
        vac_vector = []
        for vss in vskill:
            vac_vector.append(1)
        res2 = db1.select(
            "SELECT `applytable`.*,`candidate_signup`.* FROM `candidate_signup`,`applytable` WHERE `applytable`.`vacancyid`='"+id+"' AND `candidate`=`candidate_signup`.`userID`")
        if len(res2) > 0:
            for k in res2:
                res3 = db1.select("SELECT * FROM `studentskills` WHERE `userID`='" + str(k['candidate']) + "'")
                if len(res3) > 0:
                    can_vec = []
                    can_skill = []
                    for k2 in res3:
                        can_skill.append(k2['skillID'])
                    for vs in vskill:
                        sts = 0
                        if vs in can_skill:
                            sts = 1
                        can_vec.append(sts)

                    from numpy import dot
                    from numpy.linalg import norm
                    cos_sim = dot(vac_vector, can_vec) / (norm(vac_vector) * norm(can_vec))

                    if cos_sim > .4:
                        new.append(cos_sim)
                        print("------",cos_sim)
                        lis.append(k)
    print("=====",lis)

##########
    # zipped_lists = zip(new, lis)
    # sorted_zipped_lists = sorted(zipped_lists, reverse=True)
    # sorted_list1 = [element for _, element in sorted_zipped_lists]
    # print(sorted_list1)

    for kk in range(0,len(lis)-1):
        for kk1 in range(kk+1,len(lis)):
            print("+++++++",new[kk],new[kk1])
            if new[kk]<new[kk1]:
                temp=new[kk]
                new[kk]=new[kk1]
                new[kk1]=temp

                temp1=lis[kk]
                lis[kk]=lis[kk1]
                lis[kk1]=temp1
##########
    return render_template('company view candidates.html', data=lis)

@app.route('/can_applist')
def can_applist():
    res = db.select("SELECT `applytable`.*,`vacancyadd`.*,`company`.* FROM `company`,`applytable`,`vacancyadd` WHERE `applytable`.`candidate`='" + str(session['userid']) + "' AND `applytable`.`vacancyid`=`vacancyadd`.`ID` AND `vacancyadd`.`companyID`=`company`.`Id` ORDER BY `applytable`.`number` DESC")

    return render_template('candidate view applist.html', data=res)

@app.route('/candidate_profile_edit')
def candidateEdit():
    res = db.selectOne("SELECT * from candidate_signup where userId = '" + str(session['userid']) + "' ")

    return render_template('Candidate Management.html', data=res)

@app.route('/update_candidate',methods=['POST'])
def update_candidate():
    Name=request.form['CandidateName']
    Gender=request.form['CandidateGender']
    dob=request.form['CandidateDOB']
    email=request.form['Candidateemail']
    phone=request.form['CandidateMobile']
    place=request.form['CandidatePlace']
    post=request.form['CandidatePost']
    pin=request.form['CandidatePin']
    resume=request.files['CandidateFile']


    if resume is  not None:
        if resume.filename!='':
            if resume and allowed_pdffile(resume.filename):
                timestr = time.strftime("%Y%m%d-%H%M%S")
                filename = timestr + secure_filename(resume.filename)
                resume.save(os.path.join(app.config['UPLOAD_FOLDER1'], filename))


                qry = "update candidate_signup set Name = '" + Name + "', gender = '" + Gender + "', dob = '" + dob + "', place = '" + place + "', post = '" + post + "', pin = '" + pin + "', email = '" + email + "', contactnumber = '" + phone + "', resume = '" + filename + "'  where userID = '" + str(session['userid']) + "' "
                db.update(qry)
                skills = pdfresume(os.path.join(app.config['UPLOAD_FOLDER1'], filename))
                # print (skills)


                # res =  db.select("SELECT MAX (resumeskillid) from studentskills ")
                # for i in res:
                #     s = "delete from studentskills WHERE userID = '"+str(session['userid'])+"'"
                #     db.delete(s)

                db.delete("delete from studentskills where userID='"+str(session['userid'])+"'")
                for i in skills:
                    qrya = "insert into studentskills VALUES (NULL, '"+str(session['userid'])+"', '"+str(i)+"')"
                    db.insert(qrya)


        else:
            qry1 = "update candidate_signup set Name = '" + Name + "', gender = '" + Gender + "', dob = '" + dob + "', place = '" + place + "', post = '" + post + "', pin = '" + pin + "', email = '" + email + "', contactnumber = '" + phone + "'  where userID = '" + str(session['userid']) + "' "
            db.update(qry1)

    return '''<script>alert('Updated' ); window.location='/candidate_profile_edit'; </script> '''








@app.route('/edit_candidate_photo')
def edit_candidate_photo():
    return render_template('Edit_Candidate_Photo.html')

@app.route('/update_candidate_photo', methods=['POST'])
def update_candidate_photo():
    picture = request.files['fileField']

    if picture and allowed_file(picture.filename):

        timestr = time.strftime("%Y%m%d-%H%M%S")
        filename = timestr + secure_filename(picture.filename)
        picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        db.update("update candidate_signup set photo = '" + filename + "' where userID = '" + str(session['userid']) + "' ")
        return redirect('/candidate_profile_edit')

    else:
        return '''<script>alert('File Not Supported' ); window.location='/candidate_profile_edit'; </script> '''




@app.route('/apply_for_job_candidate')
def apply_for_job_candidate():

    qry= "select * from vacancyadd where status='open' ORDER BY created_date DESC "
    ress= db.select(qry)

    user_skill_count = []
    needed_skill_count = []
    score_value = []

    for row in ress:

        skills = row['skill'].replace(",", " ")

        needed_skills = []
        needed_skills = skills.split()

        user_skills = db.select("select * from studentskills where userID = '" + str(session['userid']) + "'")

        mskill = []
        result = []

        if user_skills:
            for i in user_skills:
                flag = 0
                for j in needed_skills:
                    if i['skillID'] == j:
                        mskill.append(j)
                        result.append([j, 1])
                        flag = 1
                        break
                if flag == 0:
                    result.append([i['skillID'], 0])

        user_skill_count.append(len(mskill))
        needed_skill_count.append(len(needed_skills))
        score_value.append(round((len(mskill)/len(needed_skills)*100)))

    print(user_skill_count)
    print(needed_skill_count)
    print(score_value)

    a="select vacancyid from applytable where candidate = '"+str(session['userid'])+"'"
    b=db.select(a)
    print(b)

    pred=None
    pred1=''
    from DBConnection import Db
    db1 = Db()
    res = db1.select("SELECT * FROM `skills`")
    if len(res) > 0:
        skills = []
        for rin in res:
            skills.append(rin['skillID'])
        res2 = db1.select("SELECT * FROM `vacancyadd`")
        if len(res2) > 0:
            vcy = []
            va_skills = []
            for rin in res2:
                vacancy_skill = rin['skill']
                vsks = vacancy_skill.split(',')
                vc = []
                for sk in skills:
                    sts = 0
                    ss = str(sk)
                    if ss in vsks:
                        sts = 1
                    vc.append(sts)
                va_skills.append(vc)
                vcy.append(rin['ID'])

            res3 = db1.select("SELECT * FROM `studentskills` WHERE `userID`='"+str(session['userid'])+"'")
            if len(res3) > 0:
                can_skil = []
                can_vector = []
                for sk in res3:
                    can_skil.append(sk['skillID'])

                for sk in skills:
                    sts = 0
                    ss = str(sk)
                    if ss in can_skil:
                        sts = 1
                    can_vector.append(sts)
            print(vcy)
            print("========")
            print(va_skills)
            print("========")
            print(can_vector)
            from sklearn.ensemble import RandomForestClassifier
            rfc = RandomForestClassifier()
            rfc.fit(va_skills, vcy)
            rfc_predict = rfc.predict([can_vector])
            print("======output======")
            print(rfc_predict)
            res4=db1.selectOne("SELECT * FROM `company`,`vacancyadd` WHERE `vacancyadd`.`ID`='"+str(rfc_predict[0])+"' AND `vacancyadd`.`companyID`=`company`.`Id`")
            pred=res4
            ddd=res4['skill']
            ddd2=ddd.split(',')
            for kk in ddd2:
                dc=db1.selectOne("SELECT * FROM `skills` WHERE `skillID`='"+kk+"'")
                if dc is not None:
                    pred1=pred1+""+dc['skillName']+","



    return render_template('apply_for_job_candidate.html', data=ress, skill_score = score_value, user_skill_count = user_skill_count,needed_skill_count=needed_skill_count, c=b,pr=pred,pr2=pred1)


@app.route('/check/<id>')
def check(id):

    db = Db()
    vacancy_skiils = db.selectOne("select skill from vacancyadd where ID = '"+id+"'")
    skills = vacancy_skiils['skill'].replace(",", " ")
    needed_skills = []
    needed_skills = skills.split()

    user_skills = db.select("select * from studentskills where userID = '"+str(session['userid'])+"'")
    mskill = []
    result = []
    if user_skills:
       for i in user_skills:
           flag = 0
           for j in needed_skills:
               if i['skillID'] == j:
                   mskill.append(j)
                   result.append([j,1])
                   flag = 1
                   break
           if flag == 0:
               result.append([i['skillID'],0])



    print("====total needed skills===",len(needed_skills)+1)
    print("===total matched skills===", len(mskill))
    print("===matched skills===",mskill)
    print("=====result=====",result)
    return "ok"



@app.route('/applytable/<vid>')
def applytable(vid):
    sid = str(session["userid"])
    qry= "insert into applytable VALUES (NULL, '"+sid+"', '"+vid+"', now() )"
    db.insert(qry)

    return redirect(url_for('apply_for_job_candidate'))



@app.route('/replytocandidate')
def replytocandidate():
    qry="select * from complaint where userID = '"+str(session["userid"])+"' order by date"
    res= db.select(qry)

    return render_template('replytocandidate.html', data=res)

@app.route('/candidate_complaint')
def complaintSend():
    return render_template('Candidate Complaint send.html')

@app.route('/Candidate_send_complaint_post',methods=["POST"])
def Candidate_send_complaint_post():
    Candidate_complaint=request.form['Candidate_Complaint']

    qry="INSERT INTO complaint VALUES (NULL, '"+Candidate_complaint+"','"+str(session["userid"])+"',curdate(),'NOT REPLIED','pending')"
    db.insert(qry)
    return '''<script>alert('Complaint Sent Succesfully' ); window.location='/candidate_profile'; </script> '''








############################################################################### ADMIN MODULE

@app.route('/admin_profile')
def adminProfile():
    return render_template('admin profile.html')

@app.route('/company_validation')
def companyValidation():

    qry="SELECT company.*, login.type FROM company inner join login on company.loginID = login.id ORDER by login.id DESC "
    res=db.select(qry)
    return render_template('companany validation.html',data=res)

@app.route('/company_approve/<id>')
def company_approve(id):
    qry="UPDATE login set type = 'Company' where id='"+id+"'  "
    db.update(qry)
    return '''<script>alert('Approved'); window.location='/company_validation'; </script> '''



@app.route('/company_reject/<id>')
def company_reject(id):
    qry="UPDATE login set type = 'rejected' where id='"+id+"'  "
    db.update(qry)
    return '''<script>alert('Rejected'); window.location='/company_validation'; </script> '''




# @app.route('/company_reject/<id>')
# def company_reject(id):
#     a=Db()
#     qry="DELETE from login where userName ='"+str(session['usrnm1'])+"'  "
#     a.update(qry)
#     qry1="DELETE from company_signup WHERE Id = '"+id+"' "
#     a.update(qry1)
#     return




@app.route('/view_user')
def viewUser():

    qry = "SELECT candidate_signup.*, login.type FROM candidate_signup inner join login on candidate_signup.loginID = login.id ORDER by login.id ASC"
    res = db.select(qry)

    return render_template('view user.html',data=res)

@app.route('/view_complaint_admin')
def viewComplaint():
    qry = "SELECT complaint.* FROM complaint WHERE status='pending' ORDER by ID ASC"
    res = db.select(qry)
    return render_template('view complaint admin.html', data=res)

@app.route('/adminReply/<id>')
def adminReply(id):
    session['compid']=id
    return render_template('admin Complaint Reply.html')

@app.route('/adminReplay_post', methods=['POST'])
def adminReplay_post():
    rep=request.form['complaintReply']
    d=Db()
    qry="update complaint set reply='"+rep+"',status='replied' where ID='"+str(session['compid'])+"'"
    res=d.update(qry);
    return '''<script>alert('Replied Succesfully' ); window.location='/view_complaint_admin'; </script> '''



@app.route('/more_infoc/<id>')
def more_infoc(id):
    qry = "SELECT * FROM `candidate_signup` WHERE `userID`='"+id+"'"
    res = db.selectOne(qry)
    res2=db.select("SELECT * FROM `skills`,`studentskills` WHERE `studentskills`.`userID`='"+id+"' AND `studentskills`.`skillID`=`skills`.`skillID`")
    return render_template('more_info_candidate.html', data=res,skill=res2)



##################################################################
################################################################# REGISTRATION

@app.route('/company_reg')
def companyReg():
    return render_template('reg1.html')

@app.route('/Company_Sign_up_post',methods=["POST"])
def Company_Sign_up_post():
    Name=request.form['Name']
    Place=request.form['Place']
    Post=request.form['Post']
    pin=request.form['pin']
    email=request.form['email']
    website=request.form['website']
    phone=request.form['phone']
    username=request.form['username']
    password=request.form['password']
    confirmpassword=request.form['confirmpassword']
    picture=request.files['photo']

    if picture and allowed_file(picture.filename):
        timestr = time.strftime("%Y%m%d-%H%M%S")
        filename = timestr+secure_filename(picture.filename)
        picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    qr = "insert into login VALUES(NULL,'" + username + "','" + password + "','pending') "
    lid=db.insert(qr)

    qry="insert into company VALUES(NULL,'"+Name+"','"+Place+"','"+Post+"','"+pin+"','"+email+"','"+website+"','"+phone+"','"+filename+"','"+str(lid)+"') "
    db.insert(qry)
    return '''<script>alert('Registration Successful and waiting for admin aprove' ); window.location='/'; </script> '''






@app.route('/candidate_reg')
def candidateReg():
    return render_template('reg.html')


@app.route('/Candidate_Sign_up_post',methods=["POST"])
def Candidate_Sign_up_post():
    Candidate_Name=request.form['Candidate_Name']
    Candidate_Gender=request.form['Candidate_Gender']
    Candidate_DOB=request.form['Candidate_DOB']
    Candidate_email=request.form['Candidate_email']
    Candidate_Mobile=request.form['Candidate_Mobile']
    Candidate_Place=request.form['Candidate_Place']
    Candidate_Post=request.form['Candidate_Post']
    Candidate_Pin=request.form['Candidate_Pin']
    Candidate_photo=request.files['Candidate_photo']
    Candidate_username=request.form['Candidate_Username']
    Candidate_Password=request.form['Candidate_Password']
    Candidate_PasswordConfirm=request.form['Candidate_PasswordConfirm']


    if Candidate_photo and allowed_file(Candidate_photo.filename):
        timestr = time.strftime("%Y%m%d-%H%M%S")
        filename = timestr+secure_filename(Candidate_photo.filename)
        Candidate_photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    qr = "insert into login VALUES(NULL,'" + Candidate_username + "','" + Candidate_Password + "','Candidate') "
    res=db.insert(qr)

    qry = "insert into candidate_signup VALUES(NULL,'" + Candidate_Name + "','" + Candidate_Gender + "','" + Candidate_DOB + "','" + Candidate_Place + "','" + Candidate_Post + "','" + Candidate_Pin + "','" + Candidate_email + "','" + Candidate_Mobile + "','"+filename+"','"+str(res)+"','') "
    db.insert(qry)
    return '''<script>alert('Registration Succesful'); window.location='/'; </script> '''




    return "OK"








@app.route('/Admin_complaint_reply_post',methods=["POST"])
def Admin_complaint_reply_post():
    Reply=request.form['complaintReply']

    return "OK"




#############################################################################
############################################################# resume updation
def pdfresume(abc):
    ##creating a pdf file object
    pdfFileObj = open(abc, 'rb')



    ## creating a pdf reader object
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

    ## printing number of pages in pdf file
    print(pdfReader.numPages)

    ## creating a page object

    content = ""
    for i in range(0, pdfReader.getNumPages()):
        content += pdfReader.getPage(i).extractText() + "\n"  # Extract text from page and add to content

        content = " ".join(content.replace(u"\xa0", " ").strip().split())
    # print(content)

    a=(content.find("Skills"))
    b=(content.find("project"))

    newstring = content[a:b]

    # print(newstring)

    newstring=newstring.replace(","," ")

    thislist=[]

    thislist = newstring.split()

    # print(thislist)

    newlist=[]

    res = db.select("select * from skills")
    data=res

    for i in  thislist:
        res = db.selectOne("select * from skills where skillName='"+i+"'")
        if res is not None:
                newlist.append(res['skillID'])

    # print(newlist)

    # closing the pdf file object
    pdfFileObj.close()

    return newlist





if __name__ == '__main__':
    # app.run(debug=True,host='0.0.0.0')
    app.run(debug=True)