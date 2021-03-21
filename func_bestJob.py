from DBConnection import Db
import collections  #########

db1 = Db()
res = db1.selectOne("SELECT * FROM `vacancyadd` WHERE `ID`=6")
print(res)

new = []############
lis = []
print(lis)


if res is not None:
    vskills = res['skill']
    print(vskills) ####skils

    vskills = vskills[:-1]
    print(vskills)

    vskill = vskills.split(',')
    print(vskill)

    vac_vector = []
    print(vac_vector)


    for vss in vskill:
        vac_vector.append(1)
        print(vac_vector) #1s ittt

    res2 = db1.select(
        "SELECT `applytable`.*,`candidate_signup`.* FROM `candidate_signup`,`applytable` WHERE `applytable`.`vacancyid`= 6 AND `candidate`=`candidate_signup`.`userID`")
    print(res2)  ####apply cheyytha candidates

    if len(res2) > 0:
        for k in res2:
            res3 = db1.select("SELECT * FROM `studentskills` WHERE `userID`='" + str(k['candidate']) + "'")
            print(res3) ###student skilss details

            if len(res3) > 0:
                can_vec = []
                print(can_vec)
                can_skill = []
                print(can_skill)
                for k2 in res3:
                    can_skill.append(k2['skillID'])
                    print(can_skill)  ###candid skill
                for vs in vskill:
                    sts = 0
                    if vs in can_skill:
                        sts = 1
                    can_vec.append(sts)
                    print(can_vec)   ####1 or 0 for match skills

                from numpy import dot
                from numpy.linalg import norm

                cos_sim = dot(vac_vector, can_vec) / (norm(vac_vector) * norm(can_vec))

                print(norm(vac_vector))
                print( norm(can_vec))
                print(dot(vac_vector, can_vec))
                print(cos_sim)

                if cos_sim > .4:
                    new.append(cos_sim)
                    lis.append(k)
print("=====", lis)
print(new)

sorte = {new[i]: lis[i] for i in range(len(lis))}

print(sorte)

# od = collections.OrderedDict(sorted(sorte.items(),reverse=True))
# print(od)

# sorted_d = dict(sorted(sorte.items(), key=operator.itemgetter(1),reverse=True))
# print(sorted_d)


zipped_lists = zip(new, lis)
sorted_zipped_lists = sorted(zipped_lists,reverse=True)
sorted_list1 = [element for _, element in sorted_zipped_lists]
print(sorted_list1)
print(lis)
# server_list.sort(key=lambda x: x[0]['name'], reverse=False)
