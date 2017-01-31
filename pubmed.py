# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import codecs
from nltk.tokenize import sent_tokenize
from nltk.stem.porter import *
import pymysql.cursors
import re


def getConn() :
    connection = pymysql.connect(host='127.0.0.1',
                             user='root',
                             password='pubmed',
                             db='pubmed',
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)
    return connection

    
def execSql(sql, connection) :
    with connection.cursor() as cursor:
        # Read a single record
        #print(sql)
        cursor.execute(sql)
        
def getResult(sql, connection) :
    with connection.cursor() as cursor:
        cursor.execute(sql)
        result = cursor.fetchall()
        return result
 
'''             
conn =  getConn();
sql = "insert into sentence values('%s', %d, '%s')" % ("1", 2, "test2");
print(sql)
execSql(sql, conn)
conn.close() 
'''           

def createDocXml(infile, outfile) :
    try :
        # fin = codecs.open(infile, 'rb', encoding='utf8')
        fout = codecs.open(outfile, 'w', encoding='utf8')
    finally :
          print('open')
          
         
    if not fout:
         print('open out file fail')
         exit(-1)         

    content = "<add>\n"
    doc = ""
    lineNo = 0
    fileNo = 0
    with open(infile, 'r') as fin:
      for line in fin:
        lineNo += 1
        #line = html.escape(line.strip())
        if lineNo == 1 : 
            strs = line.split("|")
            doc = "<doc><field name='id'>%s</field>" % strs[0]
            doc += "<field name='title'>%s</field>" % strs[2] 
        elif lineNo == 2 :
            strs = line.split("|")
            doc += "<field name='abstract'>%s</field>" % strs[2]
        else :
            if len(line) == 0 :
                print(fileNo)
                lineNo = 0
                doc += "</doc>\n"
                content += doc
                doc = ""
                fileNo += 1
                if fileNo >= 10000 : 
                    fout.write(content)
                    content = ""
                continue
            strs = line.split("\t")
            mention = strs[3]
            if len(strs) >= 6 :
                mention += "#" + strs[5]
            doc += "<field name='%s'>%s</field>" % (strs[4], mention)
    content += doc + "</doc>\n</add>"
    fout.write(content)
    fin.close()
    fout.close()        
    
def createSenXml(infile, outfile) :
    try :
        # fin = codecs.open(infile, 'rb', encoding='utf8')
        fout = codecs.open(outfile, 'w', encoding='utf8')
    finally :
        print('open')
        
    if not fout:
        print('open out file fail')
        exit(-1)         

    content = "<add>\n"
    doc = ""
    lineNo = 0
    fileNo = 0
    docId = ""
    sentId = 0
    mentions = list()
    sentList = list()
    menList = list()
    start = 0
    with open(infile, 'r') as fin:
        for line in fin:
            lineNo += 1
            #line = html.escape(line.strip())
            if lineNo == 1 :  # title
                sentList.clear()
                strs = line.split("|")
                docId = strs[0]
                sentList.append(strs[2])
            elif lineNo == 2 :  # abstract
                strs = line.split("|")
                senTokenList = sent_tokenize(strs[2])
                for sent in senTokenList : 
                    sentList.append(sent)
                # sentList.extend(sentTokenList)
            else :  # entities list or the end of the abstract
                if len(line) == 0 :  # the end of the abstract
                    print(fileNo)
                    for sent in sentList :
                        doc = "<doc>\n<field name='docId'>%s</field>\n" % docId
                        doc += "<field name='senId'>%d</field>\n" % sentId
                        doc += "<field name='content'>%s</field>\n</doc>\n" % sent
                        content += doc
                        
                        end = start + len(sent)
                        for mention in mentions :
                            print(mention)
                            print(start, end)
                            if int(mention[0]) <= end and int(mention[0]) >= start :
                                print(docId, sentId, start, end, mention[0])
                                menList.append([docId, sentId, mention])                   
                        sentId += 1
                        start = end + 1
                    mentions.clear()
                    sentId = 0
                    lineNo = 0
                    fileNo += 1
                    if fileNo >= 10000 : 
                        fout.write(content);
                        content = ""
                    continue
                strs = line.split("\t")
                if len(strs) >= 6 :
                    mentions.append([strs[1], strs[2], strs[3], strs[4], strs[5]])
                else :
                    mentions.append([strs[1], strs[2], strs[3], strs[4], 'NULL'])
    
    for mention in menList :
        doc = "<doc>\n<field name='docId'>%s</field>\n" % mention[0]
        doc += "<field name='senId'>%d</field>\n" % mention[1]
        doc += "<field name='gene'>%s<field>\n</doc>\n" % mention[2][2]
        content += doc             
    fout.write(content)
    fin.close()
    fout.close()      
    

def sent2DB(infile) :
    global docIds
    skip = False
    conn = getConn()
    fin = codecs.open(infile, 'rb', encoding='utf8')
    try :
        #execSql("delete from sentence", conn)
        #execSql("delete from mention", conn)
        #conn.commit()
        conn.isolation_level = None
        execSql("BEGIN", conn)
        
        lineNo = 0
        fileNo = 0
        docId = ""
        sentId = 0
        mentions = list()
        sentList = list()
        start = 0
        with open(infile, 'r') as fin:
            for line in fin:
                lineNo += 1
                if lineNo == 1 :  # title
                    sentList.clear()
                    strs = line.split("|")
                    docId = strs[0]
                    if (skip) : continue
                    sentList.append(strs[2])
                elif lineNo == 2 :  # abstract
                    if (skip) : continue
                    strs = line.split("|")
                    senTokenList = sent_tokenize(strs[2])
                    for sent in senTokenList : 
                        sentList.append(sent)
                    # sentList.extend(sentTokenList)
                else :  # entities list or the end of the abstract
                    if len(line.strip()) == 0 :  # the end of the abstract
                        if (docId == '12787486') : skip = False
                        # print(fileNo)                
                        if (fileNo % 1000 == 0) : print(fileNo)
                        count = 0
                        for sent in sentList :
                            print("%s:%s" %(docId, sentId))
                            end = start + len(sent)
                            #sent = sent.replace("'", "''").strip()
                            sent = sent.replace("\\", '\\\\').strip()
                            sent = sent.replace("'", "\\'")
                            sql = "insert into sentence(docId, sentId, content) "
                            sql += "values('%s', %d, '%s')" % (docId, sentId, sent)
                            execSql(sql, conn)                            
                            for mention in mentions :
                                if int(mention[0]) <= end and int(mention[0]) >= start :
                                    sql = "insert into mention(docId, sentId, name, type, start, end, dbId) "
                                    sql += "values('%s', %d, '%s', '%s', %d, %d, '%s')" % \
                                            (docId, sentId, mention[2], mention[3], int(mention[0]) - start, int(mention[1]) - start, mention[4])
                                    execSql(sql, conn)
                            sentId += 1
                            start = end
                            if (count > 0) :
                                start += 1 # each sentence followed by a space except for title
                            count += 1
                        mentions.clear()
                        sentId = 0
                        lineNo = 0
                        fileNo += 1
                        start = 0
                        continue
                    line = line.strip().replace("\\", "\\\\").replace("'", "\\'")
                    strs = re.split(r"[\t\s]*", line)
                    if len(strs) >= 6 :
                        mentions.append([strs[1], strs[2], strs[3], strs[4], strs[5]])
                    else :
                        mentions.append([strs[1], strs[2], strs[3], strs[4], 'NULL'])
                
    finally :
        conn.commit()
        fin.close()
        conn.close()                 


geneDict = {}

def initName2idDict():
    global geneDict
    fin = open(r"Homo_sapiens.gene_info", "r")
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
    if (geneId in geneDict.keys()) :
        return geneDict[geneId]  
    else :
        return "NULL"

def name2id(geneName) :
    global geneDict
    if (geneName in geneDict.keys()) :
        return geneDict[geneName]     
    else :
        return "NULL"    
        

def getRelation(gene1, gene2) : 
    gene1Id = name2id(gene1)
    gene2Id = name2id(gene2)
    content =''
    conn = getConn()
    sql = "select docId, sentId from "
    sql += "(select docId, sentId from mention where dbid = '%s' group by docId, sentId) as a natural join " % gene1Id
    sql += "(select docId, sentId from mention where dbid = '%s' group by docId, sentId) as b " % gene2Id
    print(sql)
    rows = getResult(sql, conn)
    for row in rows :
        sql = "select content from sentence where docId = '%s' and sentId = '%s'" \
                         % (row['docId'], row['sentId'])
        rows2 = getResult(sql, conn) 
        for r2 in rows2 :
            sql = "select start, end from mention where docId = '%s' and sentId = %s and (dbid='%s' or dbid='%s')" % (row['docId'], row['sentId'], gene1Id, gene2Id)
            rows3 = getResult(sql, conn)
            pairs = []
            for r3 in rows3 :
                pairs.append((r3['start'], r3['end']))
            sorted(pairs, key = lambda pairs : pairs[0])
            sent = r2['content']
            pre = 0
            marksent = ''
            for pair in pairs :
              marksent += sent[pre : pair[0]]
              marksent += "<gene>%s</gene>" % sent[pair[0] : pair[1]]
              pre = pair[1]
            marksent += sent[pair[1] : len(sent)]
            #print(marksent)
            #print(sent)
            content += "%s\t%s\t%s\t%s\n" %(gene1, gene2, row['docId'], marksent)
    return content
      
def getCooccurSent() :
    conn = getConn()
    fout = open(r"c:\project\pubmed\out.html", "w")
    fout.write('''
<html>
<head>
    <style>
table {
    border-collapse: collapse;
    width: 100%;
}

th, td {
    padding: 8px;
    text-align: left;
    border-bottom: 1px solid #ddd;
}

.focus {
    background-color: #4CAF50;
}
</style>
</head>
<body>
<table>''')

    stemmer = PorterStemmer()
    orgVerbs = {'regulate',
                 'interaction',
                 'reduce',
                 'correlate',
                 'degradate',
                 'increase',
                 'decrease',
                 'alter',
                 'inhibit',
                 'bind',
                 'complex',
                 'induce',
                 'affect',
                 'suppress'
                }
    verbs = set()
    for verb in orgVerbs :
        verbs.add(stemmer.stem(verb))

    sql = "select docId, sentId, count(distinct dbid) as num from mention where type='gene' group by docId, sentId"
    rows = getResult(sql, conn)
    for row in rows :
        if (row["num"] > 0):
            sql = "select content from sentence where docId='%s' and sentId=%d" \
                    % (row["docId"], row["sentId"])
            print(sql)
            row1s = getResult(sql, conn)
            content = row1s[0]["content"]
            scontent = stemmer.stem(content)
            hasVerb = False
            for verb in verbs :
                if (scontent.count(verb) > 0) :
                    hasVerb = True
                    break  
            sql = "select name,start,end,docId,sentId from mention where type='gene' and docId='%s' and sentId=%d order by start" \
                    % (row["docId"], row["sentId"])
            row1s = getResult(sql, conn)
            curr = 0
            output = ""
            for row1 in row1s :
                output += content[curr : int(row1["start"])]
                output += "<font color='red' bold>"
                output += row1["name"]
                output += "</font>"
                curr = row1["end"]

                # content = content.replace(row1["name"], "<font color='red' bold>"+row1["name"]+"</font>")
            output += content[curr : len(content)]
            fout.write("<tr class=focus><td>" + row["docId"] + ":" + str(row["sentId"]) + content + "</td></tr>")
            if (hasVerb):
                fout.write("<tr class=focus><td>" + output + "</td></tr>")
            else: 
                fout.write("<tr><td>" + output + "</td></tr>")
    fout.write("</table></body></html>")
    fout.close()
    conn.close()
    
docIds = set()    
def readDocId() :
  global docId
  fin = open(r'docId.txt') 
  for line in fin.readlines() : 
    line = line.strip()
    docIds.add(line)
    
def getAllSent() :
  fin = open("ppi.txt")
  fout = open("ppiresult2.txt", "w")
  for line in fin.readlines() :
    f = line.split('\t')
    fout.write(getRelation(f[1], f[2]))
  fin.close()
  fout.close()

import itertools
def insertCurr2DB() :
    conn = getConn()
    sql = "select docId, sentId, count(distinct dbid) as num from mention where type='gene' group by docId, sentId"
    rows = getResult(sql, conn)
    for row in rows :
        if (row['num'] > 1) :
            sql = "select distinct(dbid) from mention where docId = '%s' and sentId = '%s' and type='gene'" % (row['docId'], row['sentId'])
            rows1 = getResult(sql, conn)
            geneSet = set()
            for row1 in rows1 :
                geneSet.add(row1['dbid'])
            for pair in itertools.combinations(sorted(geneSet), 2) :
                sql = "insert into interaction(geneid1, geneid2, docId, sentId) "
                sql += "values('%s', '%s', '%s', '%s')" % (pair[0], pair[1], row['docId'], row['sentId'])
                print(sql)
                execSql(sql, conn)



#readDocId()
#sent2DB(r"/data/bioconcepts2pubtator_offsets")
#sent2DB(r"a.txt")
#sent2DB(r"/mnt/zhengqi/sample")
# print(name2id("SERPINA3"))
#  

#getCooccurSent()

# print(name2id("RECK"))

#initName2idDict()
#getRelation("RECK", "MMP9")
#getAllSent()
insertCurr2DB()

