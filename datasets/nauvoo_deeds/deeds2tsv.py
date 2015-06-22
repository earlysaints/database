from xml.dom import minidom, Node
import codecs

inxml = minidom.parse(r'deeds.xml')
outcsv = codecs.open(r'deeds.csv','w','utf-8')
outcsv.write('DEED_ID\tGRANTOR\tGRANTOR_RES\tGRANTEE\tGRANTEE_RES\tTRANSDATE\tTRANSDATE_NUM\t'+
             'PRICE\tPRICE_NUM\tPARCELS\tLOCATION\tAREA\tACK\tWITNESS\tCOMMENTS\tSOURCES\tSOURCESXML\tVERIFIED\r\n')

parcsv = codecs.open(r'parcels.csv','w','utf-8')
parcsv.write('PARCEL_ID\tFULLTEXT\tTYPE\tTOWN\tPLAT\tBLOCK\tLOT\tBLM\tRANGE\tTOWNSHIP\tSECTION\tPART\tDESCRIP\tAREA\r\n')

pdcsv = open(r'pdlink.csv','w')
pdcsv.write('LINK_ID\tPARCEL_ID\tDEED_ID\r\n')

pid=1

def att(obj,key):
    a=""
    b=obj.getElementsByTagName(key)
    if (b):
        a=b[0].childNodes[0].toxml()
    return a

for deed in inxml.getElementsByTagName('deed'):
    line=""
    did=att(deed,'DEED_ID')
    outcsv.write(did+'\t'+att(deed,'GRANTOR')+'\t'+att(deed,'GRANTOR_RES')+'\t'
                 +att(deed,'GRANTEE')+'\t'+att(deed,'GRANTEE_RES')+'\t'
                 +att(deed,'TRANSDATE')+'\t'+att(deed,'TRANSDATE_NUM')+'\t'
                 +att(deed,'PRICE')+'\t'+att(deed,'PRICE_NUM')+'\t')
#PARSE PARCELS
    pardesc="<parcels>"
    lots=deed.getElementsByTagName('LOTS')
    if (lots):
        mln = lots[0].getElementsByTagName('mln')[0]
        for ln in mln.getElementsByTagName('ln'):
            t=att(ln,'twn')
            p=att(ln,'plt')
            b=att(ln,'blk')
            l=att(ln,'lot')
            m=att(ln,'pt')
            d=att(ln,'desc')
            a=att(ln,'area')
            pardesc=pardesc+'<townparcel town="'+t+'" plat="'+p+'" block="'+b+'" lot="'+l+'" part="'+m+'" area="'+a+'">'+d+'</townparcel>'
            parcsv.write(str(pid)+'\t'+t+':'+p+':'+b+':'+l+':'+m+':'+d+'\ttown\t'+t+'\t'+p
                         +'\t'+b+'\t'+l+'\t\t\t\t\t'+m+'\t'+d+'\t'+a+'\r\n')
            pdcsv.write(str(pid)+'\t'+str(pid)+'\t'+did+'\n')
            pid=pid+1
    land=deed.getElementsByTagName('LAND')
    if (land):
        mln = land[0].getElementsByTagName('mln')[0]
        for ln in mln.getElementsByTagName('ln'):
            r=att(ln,'rng')
            t=att(ln,'twp')
            s=att(ln,'sec')
            p=att(ln,'pt')
            d=att(ln,'desc')
            a=att(ln,'area')
            pardesc=pardesc+'<plssparcel blm="4th PM" range="'+r+'" twp="'+t+'" sec="'+s+'" part="'+p+'" area="'+a+'">'+d+'</plssparcel>'
            parcsv.write(str(pid)+'\t'+p+' S'+s+' T'+t+' R'+r+' 4th PM: '+d+'\tplss\t\t\t\t\t4th PM\t'
                         +r+'\t'+t+'\t'+s+'\t'+p+'\t'+d+'\t'+a+'\r\n')
            pdcsv.write(str(pid)+'\t'+str(pid)+'\t'+did+'\n')
            pid=pid+1
    pardesc=pardesc+"</parcels>"
        
    outcsv.write(pardesc+"\t"+att(deed,'LOCATION')+'\t'+att(deed,'AREA')+'\t'
                 +att(deed,'ACK')+'\t'+att(deed,'WITNESS')+'\t'+att(deed,'COMMENTS')+'\t')
# Parse Sources
    srcxml = '<SOURCES>'
    srcarr = []
    s=deed.getElementsByTagName('SOURCE')
    if (s):
        srcxml=srcxml+s[0].toxml()
        srcarr.append(s[0].childNodes[0].data)  
    b=att(deed,'HCBOOK')
    p=att(deed,'HCPAGE')
    e=att(deed,'HCENTRY')
    d=att(deed,'HCDATE')
    n=att(deed,'HCDATE_NUM')
    if (len(b+p+e+d+n)>0):
        srcxml=srcxml+'<HC book="'+b+'" page="'+p+'" entry="'+e+'" date="'+d+'" daten="'+n+'" />'
        srcarr.append('Hancock County Deeds book '+b+' page '+p+' #'+e+' ('+d+')')
    b=att(deed,'TBOOK')
    p=att(deed,'TPAGE')
    if (len(b+p)>0):
        srcxml=srcxml+'<TLB book="'+b+'" page="'+p+'" />'
        srcarr.append('Trustees Land Book '+b+' page '+p)
    b=att(deed,'NBOOK')
    p=att(deed,'NPAGE')
    e=att(deed,'NENTRY')
    d=att(deed,'NDATE')
    n=att(deed,'NDATE_NUM')
    if (len(b+p+e+d+n)>0):
        srcxml=srcxml+'<NC book="'+b+'" page="'+p+'" entry="'+e+'" date="'+d+'" daten="'+n+'" />'
        srcarr.append('Nauvoo Municipal Court book '+b+' page '+p+' #'+e+' ('+d+')')

    srctxt="; ".join(srcarr)              
    srcxml = srcxml+'</SOURCES>'
    outcsv.write(srctxt+'\t'+srcxml+'\t'+att(deed,'VERIFIED')+'\r\n')

outcsv.flush()
outcsv.close()
parcsv.flush()
parcsv.close()
pdcsv.flush()
pdcsv.close()

