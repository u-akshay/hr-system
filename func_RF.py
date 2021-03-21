# @app.route('/apply_for_job_candidate')
# def apply_for_job_candidate():
from DBConnection import Db

db = Db()



qry= "select * from vacancyadd where status='open' ORDER BY created_date DESC "
ress= db.select(qry)

user_skill_count = []
needed_skill_count = []
score_value = []

for row in ress:

        skills = row['skill'].replace(",", " ")

        needed_skills = []
        needed_skills = skills.split()

        print("needed skills",needed_skills)

        user_skills = db.select("select * from studentskills where userID = '7'")

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
        print("mskill",mskill)
        print("result",result)





        user_skill_count.append(len(mskill))
        needed_skill_count.append(len(needed_skills))
        score_value.append(round((len(mskill)/len(needed_skills)*100)))

print(user_skill_count)
print(needed_skill_count)
print(score_value)

a="select vacancyid from applytable where candidate = '7'"
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
        # print("skills",skills)
    res2 = db1.select("SELECT * FROM `vacancyadd`")
    if len(res2) > 0:
        vcy = []
        va_skills = []
        for rin in res2:
            vacancy_skill = rin['skill']
            print("vacancy_skill",vacancy_skill)
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
            print(vsks)
            print(vc)  ####vector aaki
            print(va_skills) ##### vector append cheyth

        res3 = db1.select("SELECT * FROM `studentskills` WHERE `userID`='7'")
        if len(res3) > 0:
            can_skil = []
            can_vector = []

            for sk in res3:
                can_skil.append(sk['skillID'])
                # print("can skill",can_skil)

            for sk in skills:
                sts = 0
                ss = str(sk)
                if ss in can_skil:
                    sts = 1
                can_vector.append(sts)
                # print("can_vector",can_vector)
            print(vcy)
            print("========")
            print(va_skills)    ######## comapny skills vector
            print("========")
            print(can_vector)   ######## student skills vector

            from sklearn.ensemble import RandomForestClassifier
            rfc = RandomForestClassifier()
            rfc.fit(va_skills, vcy)
            # print(rfc.fit(va_skills, vcy))
            rfc_predict = rfc.predict([can_vector])
            print("======output======")
            print(rfc_predict)
            res4=db1.selectOne("SELECT * FROM `company`,`vacancyadd` WHERE `vacancyadd`.`ID`='"+str(rfc_predict[0])+"' AND `vacancyadd`.`companyID`=`company`.`Id`")
            pred=res4
            # print(res4)
            ddd=res4['skill']
            ddd2=ddd.split(',')
            for kk in ddd2:
                dc=db1.selectOne("SELECT * FROM `skills` WHERE `skillID`='"+kk+"'")
                if dc is not None:
                    pred1=pred1+""+dc['skillName']+","

            # print(pred1)