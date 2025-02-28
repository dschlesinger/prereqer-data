import json, re

from collections import Counter, defaultdict

def get_txt(name: str) -> str:

    text_file = ''

    with open(name, 'r') as txt:

        text_file = txt.read()

    return text_file

def merge_dicts(d1, d2):
    return {k: d1[k] + d2[k] if k in d1 and k in d2 else d1.get(k, d2.get(k)) for k in d1 | d2}

# with open('data.json', 'r') as dj:

#     data = json.load(dj)

course_prereq = {}

for i in range(1, 60):

    txt = get_txt(f'processed_courses/run3/group_{i}/response.txt').lower()

    tracks = get_txt(f'processed_courses/run3/group_{i}/track.txt').split('\n')

    b = txt.count('{') + txt.count('}')

    try:

        i_txt = "{" + "{".join(txt.split("{")[1:]).replace("```", "").replace("\n", "")

        if i_txt[-2:] != "}}":

            i_txt += "}"

        i_data = json.loads(i_txt)

        print(i, i_data.__len__(), tracks.__len__())

        for code, prereq in zip(tracks, i_data.values()):

            if code not in course_prereq:

                course_prereq[code] = {}
                
                course_prereq[code]['prereqs_computed'] = [prereq]

            else:

                course_prereq[code]['prereqs_computed'].append(prereq)

    except json.decoder.JSONDecodeError:

        print(i_txt)

        with open('broken.test.json', 'w') as broken:

            broken.write(i_txt)

        print("ERROR " + str(i))

        break

    # data = merge_dicts(data, pt)


# with open('data.json', 'w') as d:

#     json.dump(data, d)

# with open('missing.txt', 'w') as m:

#     m.write('\n'.join(missing))

with open('compiled_courses.json', 'r') as cc:

    cc_data = json.load(cc)['courses']

def merge_dicts(d1, d2):

    return {k: d1[k] | d2.get(k, {'prereqs_computed': None}) for k in d1}

with open('data.json', 'w') as store_data:

    json.dump(merge_dicts(cc_data, course_prereq), store_data)