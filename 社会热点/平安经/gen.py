def makePinAn(list, suffix):
    retString = ""
    for word in list[:-1]:
        retString += word + suffix + "，"
    retString += list[-1] + suffix + '。'
    return retString

# print(makePinAn(['一岁', '二岁']))

from num2chinese import num2chinese

file = open("/Users/anarion/Documents/Blogs/社会热点/平安经/names.txt", 'r')
rawName = file.read()
import re
nameList = re.findall(r"\[\[(.*?)\]\]", rawName)


def writePinAn(count, headStrings, step, unitString, suffix):
    begin = len(headStrings)
    count -= begin
    ageList = []
    for word in headStrings:
        ageList.append(word)
    for num in range(begin, count * step, step):
        ageList.append(num2chinese(num) + unitString)
    return makePinAn(ageList, suffix)

# print(writePinAn(100, nameList, 1, "岁"))
print(writePinAn(10, [], 52000, "元", "愉快"))