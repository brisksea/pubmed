#coding:utf-8
from django.http import HttpResponse

import urllib.request
import urllib.parse
import itertools
import pymysql.cursors
from django import template
from django.template import Context
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect


def getConn() :
    connection = pymysql.connect(host='localhost',
                             user='root',
                             password='pubmed',
                             db='pubmed',
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)
    return connection

    
def execSql(sql, connection) :
    with connection.cursor() as cursor:
        # Read a single record
        cursor.execute(sql)
        connection.commit()
        
def getResult(sql, connection) :
    with connection.cursor() as cursor:
        cursor.execute(sql)
        result = cursor.fetchall()
        return result

 
def index(request): 
    fd = open(r'/home/zhengqi/project/pubmed/web/pubmed/pubmed/index.html', 'r')   
    return HttpResponse(fd.read())
    
def query(request):
    return HttpResponse(u"<h1>Input your query<h1><form method=get action=result><input type=text name=query></input><input type=submit value=submit></input></form>")


def result3(request):
    print(request.GET['query'])
    url = 'http://127.0.0.1:8983/solr/demo/select?'
    
    para = {'indent':'on',
            'wt':'python', 
            'rows':'20000', 
            'q':request.GET['query']}
    
    connection = urllib.request.urlopen(url + urllib.parse.urlencode(para))
    response = eval(connection.read())
    geneSet = {}
    relationSet = {}
    for document in response['response']['docs']:
        #print(document)
        genes = set()
        if 'Gene' in document:
            for gene in document['Gene'] :
                gene = gene.split('#')[0]
                if (not gene in geneSet) :
                    geneSet[gene] = 1
                else :
                    geneSet[gene] += 1
                genes.add(gene)
            pairs = list(itertools.product(genes, repeat=2))
            for pair in pairs :
                if (pair in relationSet.keys()) : 
                    relationSet[pair] += 1
                else :
                    relationSet[pair] = 1   
    fp = open('c:\\project\\pubmed\\pubmed\\pubmed\\result.html')
    nodeStr = ''
    relationStr = ''
    count = 0
    for gene in geneSet.keys() :
        if (geneSet[gene] > 50) :
            nodeStr += '{category:0,name:"%s",value:%d},' % (gene, geneSet[gene])
        
    for relation in relationSet.keys() :
        count += 1
        #if count > 100 : break
        if (relationSet[relation] > 20) : 
            relationStr += '{source:"%s", target:"%s", weight:%d},' % (relation[0], relation[1], relationSet[relation])
            print(relationSet[pair])
    t = template.Template(fp.read())
    fp.close()
    rstr = t.render(Context({'geneSet':nodeStr, 'geneRelations':relationStr, 'query':request.GET['query']}))
    #rstr = t.render(Context({'geneSet':'', 'geneRelations':''}))
    
    return HttpResponse(rstr)
    


def sent1(request):
    gene1 = request.GET['gene1']
    gene2 = request.GET['gene2']
    conn = getConn()
    sql = "select docId, sentId from geneIntact where gene1 = '%s' and gene2 = '%s'" %(gene1, gene2)
    rows = getResult(sql, conn) 
    content = '<html><head><link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous"></head>'
    content += '<body><h3>Interaction between %s and %s</h1>' %(gene1, gene2)
    content += '<ul class="list-group">'
    for row in rows :
        sql = "select content from sentence where docId = '%s' and sentId = '%s'" \
                         % (row['docId'], row['sentId'])
        rows2 = getResult(sql, conn) 
        for r in rows2 :
            content += '<il class="list-group-item">' + r['content'] + "</il>"
            
    content += '</ul></body></html>'
    content = content.replace(gene1, '<mark>%s</mark>' % gene1)
    content = content.replace(gene2, '<mark>%s</mark>' % gene2)
    return HttpResponse(content)   
         
def sent11(request):
    gene1 = request.GET['gene1']
    gene2 = request.GET['gene2']
    conn = getConn()
    sql = "select docId, sentId from "
    sql += "(select docId, sentId from mention where name = '%s' group by docId, sentId) as a natural join " % gene1
    sql += "(select docId, sentId from mention where name = '%s' group by docId, sentId) as b " % gene2
    print(sql)
    rows = getResult(sql, conn) 
    content = '<html><head><link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous"></head>'
    content += '<body><h3>Interaction between %s and %s</h1>' %(gene1, gene2)
    content += '<ul class="list-group">'
    for row in rows :
        sql = "select content from sentence where docId = '%s' and sentId = '%s'" \
                         % (row['docId'], row['sentId'])
        rows2 = getResult(sql, conn) 
        for r in rows2 :
            content += '<il class="list-group-item">' + r['content'] + "</il>"
            
    content += '</ul></body></html>'
    content = content.replace(gene1, '<mark>%s</mark>' % gene1)
    content = content.replace(gene2, '<mark>%s</mark>' % gene2)
    return HttpResponse(content)      

def result4(request):
    conn = getConn()
    sql = "select gene1, gene2, docId, sentId from geneIntact"
    rows = getResult(sql, conn)
    relationSet = {}
    geneSet = {}
    for row in rows :
        if (not row['gene1'] in geneSet) :
            geneSet[row['gene1']] = 1
        else :
            geneSet[row['gene1']] += 1
            
        if (not row['gene2'] in geneSet) :
            geneSet[row['gene2']] = 1
        else :
            geneSet[row['gene2']] += 1   
        
        pair = (row['gene1'], row['gene2'])
        if (pair in relationSet.keys()) : 
            relationSet[pair] += 1
        else :
            relationSet[pair] = 1   
    fp = open('c:\\project\\pubmed\\pubmed\\pubmed\\result.html')
    nodeStr = ''
    relationStr = ''
    count = 0
    for gene in geneSet.keys() :
        if (geneSet[gene] > 0) :
            nodeStr += '{category:0,name:"%s",value:%d},' % (gene, geneSet[gene])
        
    for relation in relationSet.keys() :
        count += 1
        #if count > 100 : break
        if (relationSet[relation] > 0) : 
            relationStr += '{source:"%s", target:"%s", weight:%d},' % (relation[0], relation[1], relationSet[relation])
            print(relationSet[pair])
    t = template.Template(fp.read())
    fp.close()
    rstr = t.render(Context({'geneSet':nodeStr, 'geneRelations':relationStr, 'query':request.GET['query']}))
    #rstr = t.render(Context({'geneSet':'', 'geneRelations':''}))
    
    return HttpResponse(rstr)

def sent(request):
    gene1 = request.GET['gene1']
    gene2 = request.GET['gene2']
    if (gene1 > gene2) :
        tmp = gene1
        gene1 = gene2
        gene2 = tmp
        
    conn = getConn();
    sql = "select interaction.docId as docId, interaction.sentId as sentId, content from interaction, sentence "
    sql += "where geneid1='%s' and geneid2='%s' and interaction.docId = sentence.docId and interaction.sentId = sentence.sentId" % (gene1, gene2)
    rows = getResult(sql, conn)
    content = '<html><head><link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous"><style>gene{color: red;font: bold;}</style></head>'
    content += '<body><h3>Interaction between %s and %s</h1>' %(gene1, gene2)
    content += '<ul class="list-group">'
    for row in rows :
        content += "<il class='list-group-item'><a href='https://www.ncbi.nlm.nih.gov/pubmed/%s'>%s</a>:%s</il>" % (row['docId'], row['docId'], row['content'])         
    content += '</ul></body></html>'
    return HttpResponse(content)        
        
    
    
    


def sent2(request):
    gene1 = request.GET['gene1']
    gene2 = request.GET['gene2']
    fin = open(r"/home/zhengqi/project/pubmed/ppiresult.txt")
    rows = []
    for line in fin.readlines() :
         sgene1, sgene2, pid, sent = line.split("\t")
         #if ((sgene1 == gene1 and sgene2 == gene2) or (sgene1 == gene2 and sgene2 == gene1)) :
         if (gene1 == gene1) :
            rows.append("<gene>%s</gene>:<gene>%s</gene>:<a href='https://www.ncbi.nlm.nih.gov/pubmed/%s'>%s</a>:%s" % (sgene1, sgene2, pid, pid, sent))
    content = '<html><head><link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous"><style>gene{color: red;font: bold;}</style></head>'
    content += '<body><h3>Interaction between %s and %s</h1>' %(gene1, gene2)
    content += '<ul class="list-group">'
    for row in rows :
        content += '<il class="list-group-item">' + row + "</il>"            
    content += '</ul></body></html>'
    fin.close()
    return HttpResponse(content) 

def result(request):
    disease = request.GET['query']
    conn = getConn()
    sql = "select distinct docId from mention where type='disease' and name like '%%%s%%'" % disease
    print(sql)
    rows = getResult(sql, conn)
    docIds = list()
    docStr = ''
    count = 0
    for row in rows :
        if count > 0 :
            docStr += ','
        docIds.append(row['docId'])
        docStr += row['docId']
        count += 1
    
    #if count == 0 : return HttpResponse("No result for disease : %s\b" % disease)
    geneDict = {}
    sql = "select name, count(*) as num from mention where type='gene' and docId in (%s) group by name" % docStr
    print(sql)
    rows = getResult(sql, conn)
    nodeStr = ''
    for row in rows :
        geneDict[row['name']] = row['num']
    count = 0
    for gene in geneDict.keys() :
        if geneDict[gene] > 50 :
            count += 1
            if count > 1 : nodeStr += ","
            nodeStr += '{category:0,name:"%s",value:%d}' % (gene, geneDict[gene])
    
    sql = "select a.name as gene1, b.name as gene2 from " 
    sql += "(select docId, sentId, name from mention where type = 'gene' and docId in (%s) group by docId, sentId, name) as a, " % docStr
    sql += "(select docId, sentId, name from mention where type = 'gene' and docId in (%s) group by docId, sentId, name) as b " % docStr
    sql += "where a.docId = b.docId and a.sentId = b.sentId and a.name < b.name "
    print(sql)
    rows = getResult(sql, conn)
    relationSet = {}
    for row in rows :                   
        pair = (row['gene1'], row['gene2'])
        if (pair in relationSet.keys()) : 
            relationSet[pair] += 1
            
        else :
            relationSet[pair] = 1     
    
    relationStr = ''
    count = 0
    for relation in relationSet.keys() :        
        #if count > 100 : break
        if (relationSet[relation] > 20) :
            count += 1
            if count > 1 : relationStr += "," 
            relationStr += '{source:"%s", target:"%s", weight:%d}' % (relation[0], relation[1], relationSet[relation])
    
    fp = open('c:\\project\\pubmed\\pubmed\\pubmed\\result.html')
    t = template.Template(fp.read())
    rstr = t.render(Context({'geneSet':nodeStr, 'geneRelations':relationStr, 'query':request.GET['query']}))
    conn.close()
    return HttpResponse(rstr)

def gene(request):
    gene = request.GET['gene']
    conn = getConn()
    sql = "select docId, sentId from mention where type='gene' and name='%s'" % gene
    print(sql)
    rows = getResult(sql, conn)
    content = '<html><head><link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous"></head>'
    content += '<body><h3>Sentences contain %s</h1>' % gene
    content += '<ul class="list-group">'
    for row in rows :
        sql = "select content from sentence where docId = '%s' and sentId = '%s'" \
                         % (row['docId'], row['sentId'])
        rows2 = getResult(sql, conn) 
        for r in rows2 :
            content += '<il class="list-group-item">' + r['content'] + "</il>"
            
    content += '</ul></body></html>'
    content = content.replace(gene, '<mark>%s</mark>' % gene)
    return HttpResponse(content)   


geneDict = {}

def getRelation(gene1, gene2) : 
    gene1Id = name2id(gene1)
    gene2Id = name2id(gene2)
    conn = getConn()
    sql = "select docId, sentId from "
    sql += "(select docId, sentId from mention where name = '%s' group by docId, sentId) as a natural join " % gene1Id
    sql += "(select docId, sentId from mention where name = '%s' group by docId, sentId) as b " % gene2Id
    rows = getResult(sql, conn)
    for row in rows :
        sql = "select content from sentence where docId = '%s' and sentId = '%s'" \
                         % (row['docId'], row['sentId'])
        rows2 = getResult(sql, conn) 
        for r in rows2 :
            print(r['content'])
    return len(rows)

def initName2idDict():
    fin = open(r"C:\0research\data\Homo_sapiens.gene_info", "r")
    lineno = 0
    for line in fin :
        lineno += 1
        if (lineno == 1) : continue
        fields = line.split()
        geneDict[fields[2]] = fields[1]
        
def initId2nameDict():
    global geneDict
    fin = open(r"C:\0research\data\Homo_sapiens.gene_info", "r")
    lineno = 0
    for line in fin :
        lineno += 1
        if (lineno == 1) : continue
        fields = line.split()
        geneDict[fields[1]] = fields[2]        
                       
def id2name(geneId) :
    global geneDict
    return geneDict[geneId]  

def name2id(geneName) :
    global geneDict
    return geneDict[geneName]  
             
def uploadfile(request):
    initName2idDict()
    f=request.FILES['ppifile']
    ppistr = ""
    for line in f.readlines():
        fields = line.decode("ascii").rstrip('\r\n').split('\t')
        ppistr += "%s : %s <br>" % (fields[0], fields[1])
        print("%s : %s <br>" % (fields[0], fields[1]))
        getRelation(fields[0], fields[1])
    return HttpResponse(ppistr)

def ppinetwork(request) :
    fin = open(r"/home/zhengqi/project/pubmed/ppi.txt")
    geneSet = set()
    relationSet = {}
    for line in fin.readlines() :
        fields = line.strip().split('\t')
        gene1 = fields[1]
        gene2 = fields[2]
        type = fields[3]
        geneSet.add(gene1)
        geneSet.add(gene2)
        relationSet[(gene1, gene2)] = type
    nodeStr = ''
    count = 0
    for gene in geneSet :
        count += 1
        if count > 1 : nodeStr += "," 
        nodeStr += '{category:0,name:"%s",value:1}' % gene  
    
    relationStr = ''
    count = 0
    for relation in relationSet.keys() :        
        count += 1
        if count > 1 : relationStr += "," 
        relationStr += '{source:"%s", target:"%s", weight:%s, lineStyle:{normal:{color:\'blue\'}}}' % (relation[0], relation[1], '1')
        #relationStr += '{source:"%s", target:"%s", weight:%s, lineStyle:{normal:{color:\'blue\'}}}' % (relation[0], relation[1], relationSet[relation])
        #relationStr += '{source:"%s", target:"%s", weight:%s}' % (relation[0], relation[1], relationSet[relation])
    
    fp = open(r'/home/zhengqi/project/pubmed/web/pubmed/pubmed/result.html')
    t = template.Template(fp.read())
    rstr = t.render(Context({'geneSet':nodeStr, 'geneRelations':relationStr, 'query':'query'}))
    fin.close()
    fp.close()
    return HttpResponse(rstr)    


    
