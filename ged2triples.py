import csv, re
inged = open(r'c:\data\earlysaints\ward-watt\iowa.ged', 'rU')
outcsv = open(r'c:\data\earlysaints\ward-watt\iowa.csv', 'w')
fields=['id','assert_type','subject','predicate','object']
csvwriter = csv.DictWriter(outcsv, fieldnames=fields,lineterminator='\n')
csvwriter.writeheader()
inlines = inged.readlines()
id=1
lastlevel=-1
last=[-1,-1,-1,-1,-1,-1,-1]

preds = { 'NAME':'name', 'GIVN':'given name', 'SURN':'family name','SOUR':'supported by',
          'SEX':'gender', 'BIRT':'was born', 'PLAC':'location text', 'DATE':'date text',
          'DEAT':'died', 'BURI':'was buried', 'PAGE':'fragment', 'QUAY':'*quality',
          'EVEN':'had event', 'TYPE':'event type', 'NOTE':'has note', 
          '_UID':'universal ID', 'CHAN':'*last modified',
          'TIME':'*time text', 'FAMS':'spouse in family', 'FAMC':'child in family',
          'CENS':'*census', 'RESI':'residence', 'HUSB':'has husband', 'WIFE':'has wife',
          'CHIL':'has child', 'MARR':'was married', 'TITL':'name'
          }
entities = { 'INDI':'person', 'NOTE':'*note', 'FAM':'family' }
rows = {}
for line in inlines:
    m = re.match(r'^\D*(\d+) (\S+)( (.+))?$',line)
    level = m.group(1)
    lev = int(level)
    pred = m.group(2)
    if (m.group(3)):
        value = m.group(4).strip()
    else:
        value = ""
    if (lev == 0):
        if (len(rows) > 0):
            csvwriter.writerow(rows[last[0]])
            k=rows.keys()
            k.sort()
            for i in k:
                csvwriter.writerow(rows[i])
        rows = {}
        id2 = pred.strip('@')
        if (value in ('REPO','SOUR')):
            rows[id2]={"id":id2,"assert_type":"artifact","subject":id2,"predicate":"common name","object":""}
        else:
            rows[id2]={"id":id2,"assert_type":"entity","subject":id2,"predicate":"common name","object":""}
            if (value in entities.keys()):
                value = entities[value]
            rows[id]={"id":id,"assert_type":"property","subject":id2,"predicate":"entity type","object":value}
    else:
        sub = last[lev-1]
        id2 = id
        if (pred == 'NAME' and rows[sub]["predicate"]=="common name"):
            rows[sub]["object"] = value
        if (pred == 'ABBR' and rows[sub]["predicate"]=="common name"):
            rows[sub]["object"] = value
            continue
        if (pred == 'CONT'):
            rows[sub]["object"] = rows[sub]["object"] + '|' + value
            continue
        if (pred == 'CONC'):
            rows[sub]["object"] = rows[sub]["object"] + ' ' + value
            continue
        if (pred in preds.keys()):
            pred = preds[pred]
        rows[id]={"id":id, "assert_type":"property", "subject":sub, "predicate":pred,"object":value}
    last[lev] = id2
    id=id+1

inged.close()
outcsv.close()
    
