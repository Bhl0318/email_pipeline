# -*- coding: UTF-8 -*-
import requests
import pymysql
import json,os,re
from models import *
import pymssql
from sqlalchemy import func, or_, and_, text

WikiKey = {"20724":{"key":"20724","pid":"1805540"},
           "20633":{"key":"dahua","pid":"7738411"},
           "20664":{"key":"20664","pid":"1805542"},
           "20779":{"key":"20779","pid":"18735049"},
           "20615":{"key":"didi","pid":"7738553"},
           "20801":{"key":"kraajr","pid":"18723928"},
           "20673":{"key":"20673","pid":"18284594"},
           "20749":{"key":"20749","pid":"7739889"},
           "20618":{"key":"ui","pid":"7739614"},
           "20735":{"key":"alipay","pid":"7738524"},
           "20608":{"key":"aftershokz","pid":"7738416"},
           "20758":{"key":"20758","pid":"18730123"},
           "88888":{"key":"~hlbi","pid":"1817102"},
           "other":{"key":"otherclients","pid":"38472474"}
           }



ZUCON ="""
<ac:layout><ac:layout-section ac:type="two_right_sidebar"><ac:layout-cell><h3>基本情况：</h3><table class="relative-table wrapped" style="width: 96.7409%;"><colgroup><col style="width: 13.1579%;" /><col style="width: 86.8421%;" /></colgroup><tbody><tr><th>案件名称</th><td></td></tr><tr><th>发明人（以优先权为准）</th><td><br /></td></tr><tr><th colspan="1">IPC分类</th><td colspan="1"><br /></td></tr><tr><th colspan="1">优先权日期</th><td colspan="1"><br /></td></tr><tr><th colspan="1">案件KOD目录&nbsp;</th><td colspan="1"></td></tr></tbody></table><h3><span>撰写类型</span></h3><table class="relative-table wrapped" style="width: 96.7409%;"><colgroup><col style="width: 13.1579%;" /><col style="width: 86.8421%;" /></colgroup><tbody><tr><th><strong>撰写类型</strong></th><td><ac:task-list>
<ac:task>
<ac:task-id>73</ac:task-id>
<ac:task-status>incomplete</ac:task-status>
<ac:task-body>CN</ac:task-body>
</ac:task>
<ac:task>
<ac:task-id>74</ac:task-id>
<ac:task-status>incomplete</ac:task-status>
<ac:task-body>PCT/US/EP&nbsp; &nbsp;</ac:task-body>
</ac:task>
<ac:task>
<ac:task-id>75</ac:task-id>
<ac:task-status>incomplete</ac:task-status>
<ac:task-body>基于优先权的PCT/US/EP</ac:task-body>
</ac:task>
</ac:task-list></td></tr></tbody></table><p><br /></p><p><span style="font-size: 16.0px;font-weight: bold;letter-spacing: -0.006em;">交底、技术理解、预检索和相关申请</span></p><table class="relative-table wrapped" style="width: 96.7409%;"><colgroup><col style="width: 13.1579%;" /><col style="width: 86.8421%;" /></colgroup><tbody><tr><th><strong>交底文件</strong></th><td><ac:task-list>
<ac:task>
<ac:task-id>1</ac:task-id>
<ac:task-status>incomplete</ac:task-status>
<ac:task-body>下级技术理解页面中（优选的方式。请将该页面移至本页面下级）</ac:task-body>
</ac:task>
<ac:task>
<ac:task-id>2</ac:task-id>
<ac:task-status>incomplete</ac:task-status>
<ac:task-body>单独下级页面&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;</ac:task-body>
</ac:task>
<ac:task>
<ac:task-id>3</ac:task-id>
<ac:task-status>incomplete</ac:task-status>
<ac:task-body>KOD文件夹中</ac:task-body>
</ac:task>
<ac:task>
<ac:task-id>4</ac:task-id>
<ac:task-status>incomplete</ac:task-status>
<ac:task-body>无交底文件</ac:task-body>
</ac:task>
</ac:task-list></td></tr><tr><th colspan="1">技术理解</th><td colspan="1"><ac:task-list>
<ac:task>
<ac:task-id>5</ac:task-id>
<ac:task-status>incomplete</ac:task-status>
<ac:task-body>下级技术理解页面（优选的方式。请将该页面移至本页面下级）</ac:task-body>
</ac:task>
<ac:task>
<ac:task-id>6</ac:task-id>
<ac:task-status>incomplete</ac:task-status>
<ac:task-body>交底足够清晰，无单独技术理解内容</ac:task-body>
</ac:task>
</ac:task-list></td></tr><tr><th colspan="1">发明人访谈</th><td colspan="1"><ac:task-list>
<ac:task>
<ac:task-id>7</ac:task-id>
<ac:task-status>incomplete</ac:task-status>
<ac:task-body>技术清晰，未进行发明人访谈</ac:task-body>
</ac:task>
<ac:task>
<ac:task-id>8</ac:task-id>
<ac:task-status>incomplete</ac:task-status>
<ac:task-body>待进行访谈</ac:task-body>
</ac:task>
<ac:task>
<ac:task-id>9</ac:task-id>
<ac:task-status>incomplete</ac:task-status>
<ac:task-body>已访谈，记录在交底文件中</ac:task-body>
</ac:task>
<ac:task>
<ac:task-id>10</ac:task-id>
<ac:task-status>incomplete</ac:task-status>
<ac:task-body>已访谈，记录在技术理解中（建议方式。请将该页面移至本页面下级）</ac:task-body>
</ac:task>
<ac:task>
<ac:task-id>11</ac:task-id>
<ac:task-status>incomplete</ac:task-status>
<ac:task-body>已访谈，单独下级访谈记录页面（请将该页面移至本页面下级）</ac:task-body>
</ac:task>
</ac:task-list></td></tr><tr><th colspan="1">预检索</th><td colspan="1"><ac:task-list>
<ac:task>
<ac:task-id>26</ac:task-id>
<ac:task-status>incomplete</ac:task-status>
<ac:task-body>按客户要求不进行预检索</ac:task-body>
</ac:task>
<ac:task>
<ac:task-id>27</ac:task-id>
<ac:task-status>incomplete</ac:task-status>
<ac:task-body>客户提供预检索信息（请在本页面下级建立页面保存）</ac:task-body>
</ac:task>
<ac:task>
<ac:task-id>28</ac:task-id>
<ac:task-status>incomplete</ac:task-status>
<ac:task-body>我方进行预检索（检索记录见下级页面）</ac:task-body>
</ac:task>
</ac:task-list></td></tr><tr><th colspan="1">相关申请</th><td colspan="1"><ac:task-list>
<ac:task>
<ac:task-id>76</ac:task-id>
<ac:task-status>incomplete</ac:task-status>
<ac:task-body>无相关申请</ac:task-body>
</ac:task>
<ac:task>
<ac:task-id>77</ac:task-id>
<ac:task-status>incomplete</ac:task-status>
<ac:task-body>客户提供相关申请（请在本页面下级建立页面保存）</ac:task-body>
</ac:task>
</ac:task-list></td></tr></tbody></table><p class="auto-cursor-target"><br /></p></ac:layout-cell><ac:layout-cell><h3>详细记录子页面：</h3><p><strong><ac:structured-macro ac:name="children" ac:schema-version="2" ac:macro-id="e7c7af2c-39a8-4783-8bfc-ff1ece25de93"><ac:parameter ac:name="all">true</ac:parameter></ac:structured-macro></strong></p></ac:layout-cell></ac:layout-section><ac:layout-section ac:type="single"><ac:layout-cell><h3 class="auto-cursor-target">撰写阶段的相关文献</h3><p>注意：此处相关文献为<strong>已发表</strong>的论文，尚未发表的论文视为交底文件。</p><table class="relative-table wrapped"><colgroup><col style="width: 49.0px;" /><col style="width: 447.0px;" /></colgroup><tbody><tr><th class="numberingColumn">序号</th><th>客户提供的其他文献</th></tr><tr><td class="numberingColumn">1</td><td><br /></td></tr><tr><td class="numberingColumn">2</td><td><br /></td></tr><tr><td class="numberingColumn">3</td><td><br /></td></tr></tbody></table><p class="auto-cursor-target"><br /></p></ac:layout-cell></ac:layout-section></ac:layout>
"""


# 案号：project;案件标题：project_title;撰写人员：project_write
#

sqldb = sqlDb()

class CreateWikiOa():
    def __init__(self):
        self.admin = 'confluence'
        self.pwd = 'wikimaster'
        self.headers = {'content-type': "application/json","Accept": "application/json","Authorization": "Bearer <access_token>"}

    def getcusdata(self):
        data = sqldb.simpleQuery(CusSpace,CusSpace.cus_code!='')
        WikiKey = {}
        for i in data:
            WikiKey[i.cus_code] = {"key":i.s_key,"pid":i.p_id}
        return WikiKey


    def getContentByTitleres(self,title,key=False,pid=False):
        """
        :param title:指定文章标题
        :return:文章内容
        """
        headers = {'content-type': "application/json"}
        response = requests.get('http://10.10.70.90:9090/rest/api/content?title={}&start=0&limit=10&expand=space,history,body.view,metadata.labels'.format(title),
            auth=(self.admin, self.pwd),
            headers=self.headers)
        json_content = response.text
        # print('json_content:',json_content)
        parse_content = json.loads(json_content)
        return parse_content['results']
        # if parse_content['results']:
        #     id = parse_content['results'][0]['id']  # 该页面的id
        #     content = parse_content['results'][0]['body']['view']['value']  # 指定title下的内容
        #     print("content:",content)
        #     return id

    def getContentByTitle(self,project):
        """
        :param title:指定文章标题
        :return:文章内容
        """
        project_title,public = self.findprojectinfo(project)
        # customer = re.findall('[0-9]{5}',project)
        customer = project.split('-')
        WikiKey = self.getcusdata()
        if customer[0] not in WikiKey:
            customer_code = 'other'
        else:
            customer_code = customer[0]
        if project[0:1]=='5':
            customer_code = '5'
        if project[0:1]=='6':
            customer_code = '6'
        customerzu = re.findall('[0-9A-Z]{5}-[a-zA-Z0-9]{4}',project)
        zutitle = customerzu[0] + "族案件记录"
        # ================================================================
        ppdata = sqldb.simpleQuery(Project,and_(Project.project == project,or_(Project.project_type =='CN撰写',Project.project_type =='EN撰写')),limitOne=True)
        sqldb.close()
        ppar = ''
        pqc = ''
        ppm = ''
        if ppdata:
            ppar = ppdata.project_participant
            pqc = ppdata.project_qc
            ppm = ppdata.project_leader
        else:
            ppdata = sqldb.simpleQuery(Project,and_(Project.project.like(f'{customerzu[0]}%'),or_(Project.project_type =='CN撰写',Project.project_type =='EN撰写')),limitOne=False)
            sqldb.close()
            for i in ppdata:
                if i.project_participant:
                    ppar = i.project_participant
                    pqc = i.project_qc
                    ppm = i.project_leader
        # ================================================================
        if ppar or pqc or ppm:
            project_write = f"QC:{pqc};负责人:{ppm};参与人:{ppar}"
        else:
            project_write = ''
        tzudata = sqldb.simpleQuery(Project,and_(Project.project.like(f'{customerzu[0]}%'), Project.oa_remark.like("%首案%") ,Project.project_type.like("%答复及其他%")),limitOne=False)
        sqldb.close()
        tzucon = ''
        for i in tzudata:
            tzutitle = i.project_name
            tzuppar = i.project_participant
            tzupqc = i.project_qc
            tzuppm = i.project_leader
            tzucon += f"{i.project}{tzutitle}，QC:{tzupqc}；负责人：{tzuppm}；参与人：{tzuppar}<br/>"
        if tzucon:
            tzu_Wcon = tzucon
        else:
            tzu_Wcon = ''
        tzu = f"<a href='http://10.10.70.88:8086/showProZu/{project[0:10]}'>http://10.10.70.88:8086/showProZu/{project[0:10]}</a>"
        if public:
            patentlink = f"<a target='_blank' href='https://patents.google.com/patent/{public}'>{project}的申请文件</a>"
        else:
            patentlink = ''
        tzu_Link = f"<a target='_blank' href='http://10.10.70.88:8080/manage/prosummary_search?pro={customerzu[0]}'>http://10.10.70.88:8080/manage/prosummary_search?pro={customerzu[0]}</a>"

        headers = {'content-type': "application/json"}
        response = requests.get(
            'http://10.10.70.90:9090/rest/api/content?title={}&start=0&limit=10&expand=space,history,body.view,metadata.labels'.format(
                zutitle),
            auth=(self.admin, self.pwd),
            headers=self.headers)
        json_content = response.text
        parse_content = json.loads(json_content)
        wikikey = WikiKey[customer_code]
        if parse_content['results']:
            for i in parse_content['results']:
                keyresult = i['space']['key']
                wikpid = i['id']
                if keyresult == wikikey['key']:
                    fintitle = project+'-OA信息记录表'
                    project = project
                    project_title = project_title
                    if customer[0] in ['20849', '20769', '20228', '20229', '20231', '20235', '20236', '20239', '20245','20252', '20254', '20256', '20257','90009','20901'] or project[0:1] in ['5', '6']:
                        p1 = ''
                        p2 = f"""  
                                <table class="relative-table wrapped" style="width: 56.2396%;">
                                <colgroup>
                                <col style="width: 10.2665%;" />
                                <col style="width: 89.7335%;" />
                                </colgroup>
                                <tbody>
                                <tr><th colspan="1"><p>申请文件链接</p></th><td colspan="1"><strong style="text-align: left;">填写Google Patent的公开链接:{patentlink}</strong></td></tr>
                                <tr><th colspan="1"><p><strong>TIP同族信息</strong></p></th><td colspan="1">{tzu_Link}</td></tr>
                                <tr><th colspan="1">唯德同族信息</th><td colspan="1"><span style="color: rgb(23,43,77);">{tzu}</span></td></tr>
                                <tr><th colspan="1">授权状态</th><td colspan="1"><span style="color: rgb(23,43,77);"></span></td></tr>
                                </tbody></table>
                                """
                        p3 = ''
                        p4 = """ <table class="relative-table wrapped" style="width: 99.5739%;"><colgroup><col style="width: 12.3016%;" />
                        <col style="width: 87.6191%;" /></colgroup>
                        <thead>
                        <tr>
                        <th style="text-align: left;" colspan="1"><p>OA次数</p></th>
                        <th style="text-align: left;"><p><span style="color: rgb(0,0,255);">答复期限</span></p></th>
                        <th style="text-align: left;">送审记录</th>
                        </tr>
                        </thead>
                        <tbody>
                        <tr><td>OA1</td><td></td><td></td></tr>
                        <tr><td>OA2</td><td></td><td></td></tr>
                        <tr><td>OA3</td><td></td><td></td></tr></tbody>
</table>"""
                    else:
                        p1 = """ <h2>案件整体策略</h2><p>说明:下表用于案件处理过程中记录整体思路及案件最终授权结果。<br />比如：<br />1、OA1抗辩，<br />2、OA2中将权4、5及说明书[0038]上提。 后续考虑根据权9分案，等等</p> """
                        p2 = f"""  
                                <table class="relative-table wrapped" style="width: 56.2396%;">
                                    <colgroup>
                                    <col style="width: 10.2665%;" />
                                    <col style="width: 89.7335%;" />
                                    </colgroup>
                                    <tbody>
                                    <tr><th style="text-align: left;"><span style="color: rgb(0,51,102);">案号</span></th><td style="text-align: left;">{project}</td></tr>
                                    <tr><th colspan="1">案件标题</th><td colspan="1">{project_title}</td></tr>
                                    <tr><th colspan="1">公开号</th><td colspan="1">{public}</td></tr>
                                    <tr><th colspan="1">分类号</th><td colspan="1"></td></tr>
                                    <tr><th colspan="1">申请文件链接</th><td colspan="1"><strong style="text-align: left;">填写Google Patent的公开链接:{patentlink}</strong></td></tr>
                                    <tr><th colspan="1">TIP同族信息</th><td colspan="1">{tzu_Link}</td></tr>
                                    <tr><th colspan="1">唯德同族信息</th><td colspan="1"><span style="color: rgb(23,43,77);">{tzu}</span></td></tr>
                                    <tr><th colspan="1">授权状态</th><td colspan="1"><span style="color: rgb(23,43,77);"></span></td></tr>
                                    </tbody></table>
                                """
                        p3 = """<ac:layout-section ac:type="single">
                    <ac:layout-cell>
                    <p><strong>整体策略思路记录及案件授权结果</strong></p>
                    <table class="relative-table wrapped" style="width: 100.0%;"><colgroup><col style="width: 1.92997%;" /><col style="width: 87.5655%;" /><col /></colgroup><tbody><tr><th class="numberingColumn">1</th><td></td><td rowspan="4"><h3>案件授权结果：</h3><ac:task-list>
                    <ac:task>
                    <ac:task-id>65</ac:task-id>
                    <ac:task-status>incomplete</ac:task-status>
                    <ac:task-body><strong><span class="placeholder-inline-tasks">授权</span></strong></ac:task-body>
                    </ac:task>
                    <ac:task>
                    <ac:task-id>67</ac:task-id>
                    <ac:task-status>incomplete</ac:task-status>
                    <ac:task-body><strong><span class="placeholder-inline-tasks">放弃</span></strong></ac:task-body>
                    </ac:task>
                    </ac:task-list></td></tr><tr><th class="numberingColumn">2</th><td><br /></td></tr><tr><th class="numberingColumn">3</th><td><br /></td></tr><tr><th class="numberingColumn" colspan="1">4</th><td colspan="1"><br /></td></tr></tbody>
                    </table>
                    <p class="auto-cursor-target"><br /></p></ac:layout-cell></ac:layout-section>"""
                        p4 = """<p><span>审查意见链接：将审查意见在<a href="http://10.10.70.88:8058/demand/word">http://10.10.70.88:8058/demand/word</a>生成Wiki页面（该页面同时提供了Word-PDF转换工具）。<span style="color: rgb(0,51,102);">Wiki父页面链接可以是本案OA信息记录表页面</span>。</span></p>
                                <p><span>对比文件链接：<span style="color: rgb(0,51,102);">可以是Google Patent链接,基于正式文本进行核对，填写时应与审查意见中的简称相对应。</span></span></p><p><span><span style="color: rgb(0,51,102);">请根据审查意见，对于存在的情况/问题进行勾选。各项含义为：是否存在可授权权要，存在请勾选。</span></span></p>
                                <table class="relative-table wrapped" style="width: 100.0%;">
                                <colgroup>
                                </colgroup><thead>
                                <tr>
                                <th style="text-align: left;" colspan="1"><p>OA次数</p></th>
                                <th colspan="1">OA收文日</th>
                                <th style="text-align: left;"><p><span style="color: rgb(0,51,102);">期限</span></p></th>
                                <th colspan="1">存在可授权</th>
                                <th colspan="1"><p>对比文件链接（请上传到对应单元格内，<span><span style="color: rgb(0,51,102);"><span style="color: rgb(255,0,0);"><strong>根据案件级别判断，</strong></span></span></span><span><span style="color: rgb(0,51,102);"><span style="color: rgb(255,0,0);"><strong>如无必要可不提供</strong></span></span></span>）</p></th>
                                <th style="text-align: left;">送审记录</th>
                                </tr></thead><tbody>
                                <tr><td style="text-align: left;" colspan="1"><p>OA1</p></td><td colspan="1"></td><td style="text-align: left;"></td><td colspan="1"><ac:task-list>
                                <ac:task>
                                <ac:task-id>106</ac:task-id>
                                <ac:task-status>incomplete</ac:task-status>
                                <ac:task-body><span>&nbsp;</span></ac:task-body>
                                </ac:task>
                                </ac:task-list></td><td colspan="1"><p><br /></p></td><td></td></tr><tr><td colspan="1">OA2</td><td colspan="1"><br /></td><td colspan="1"><br /></td><td colspan="1"><ac:task-list>
                                <ac:task>
                                <ac:task-id>107</ac:task-id>
                                <ac:task-status>incomplete</ac:task-status>
                                <ac:task-body><span>&nbsp;</span></ac:task-body>
                                </ac:task>
                                </ac:task-list></td><td colspan="1"><p><br /></p></td><td></td></tr><tr><td colspan="1">OA3</td><td colspan="1"><br /></td><td colspan="1"><div class="content-wrapper"><p><br /></p></div></td><td colspan="1"><ac:task-list>
                                <ac:task>
                                <ac:task-id>108</ac:task-id>
                                <ac:task-status>incomplete</ac:task-status>
                                <ac:task-body><span>&nbsp;</span></ac:task-body>
                                </ac:task>
                                </ac:task-list></td><td colspan="1"><br /></td><td></td></tr></tbody>
                                </table>"""
                    TempletWiki = f"""
                    <ac:layout>
                    <ac:layout-section ac:type="two_right_sidebar">
                    <ac:layout-cell>
                    <p class="auto-cursor-target"><br /></p>
                    <ac:structured-macro ac:name="expand" ac:schema-version="1" ac:macro-id="31af0584-1bbd-44c9-afaf-86b7846ec5f3">
                    <ac:parameter ac:name="title">模板使用说明：</ac:parameter>
                    <ac:rich-text-body>
                    <p><strong>模板使用说明：</strong></p>
                    <p><strong><span style="color: rgb(17,31,44);"><span style="color: rgb(17,31,44);">1.&nbsp;</span><ac:inline-comment-marker ac:ref="90f239e7-ce0d-42f7-8c0d-e99fc6d13a22"><span style="color: rgb(17,31,44);">请复制本页至</span>同族记录</ac:inline-comment-marker><ac:inline-comment-marker ac:ref="90f239e7-ce0d-42f7-8c0d-e99fc6d13a22">页面下（同族页面建立后隔天会自动生成本页面）</ac:inline-comment-marker><span style="color: rgb(23,43,77);">，标题格式为：案号-OA信息记录表，</span></span></strong></p><p class="auto-cursor-target" style="margin-left: 30.0px;"><strong><span style="color: rgb(17,31,44);"><span style="color: rgb(23,43,77);">例如：</span></span><span style="color: rgb(255,0,0);">20618-0017US01-OA信息记录表</span></strong></p><p class="auto-cursor-target"><strong><span style="color: rgb(17,31,44);"><span style="color: rgb(23,43,77);">2. 对于审查意见及其他只有文件而没有Web页面的资料，请通过以下工具页面<ac:inline-comment-marker ac:ref="b31a4cb6-d409-4add-b6c9-607014420114">转换并生成Wiki页面（如无以下三者需求，可以不生成该页面，需求：1、页面翻页；2、文本复制；3、文本搜索）</ac:inline-comment-marker>：</span></span></strong></p><p class="auto-cursor-target" style="margin-left: 30.0px;"><strong><span style="color: rgb(17,31,44);"><span style="color: rgb(23,43,77);"><a href="http://10.10.70.88:8058/demand/word">http://10.10.70.88:8058/demand/word</a>&nbsp;</span></span></strong><strong style="letter-spacing: 0.0px;"><span style="color: rgb(17,31,44);"><span style="color: rgb(23,43,77);">&nbsp;&nbsp;</span></span></strong></p><p class="auto-cursor-target" style="margin-left: 30.0px;"><br /></p><strong><ac:link><ri:page ri:space-key="~yli" ri:content-title="OA答复策略的参考规范" /></ac:link></strong></ac:rich-text-body></ac:structured-macro><p class="auto-cursor-target"><span style="color: rgb(255,0,0);"><strong><ac:inline-comment-marker ac:ref="617054d5-4bea-477c-b7b5-9d7a9f231f67">注意：</ac:inline-comment-marker></strong></span></p><ul><li class="auto-cursor-target"><span style="color: rgb(255,0,0);"><strong>本页所提供链接仅用于方便快速查看、定位、搜索，</strong></span></li><li class="auto-cursor-target"><span style="color: rgb(255,0,0);"><strong>由于在格式转换时可能不完全准确，因此最终准备答复意见时请核对正式文本。</strong></span></li><li class="auto-cursor-target"><span style="color: rgb(255,0,0);"><strong>答复策略需要与答复稿一致！！！</strong></span></li></ul>
                    {p1}
                    </ac:layout-cell>
                    <ac:layout-cell><p><strong>本页目录：</strong></p><p><ac:structured-macro ac:name="toc" ac:schema-version="1" ac:macro-id="0ddfca01-e5d5-4bc7-b7d3-50ec61f7aa5e"><ac:parameter ac:name="maxLevel">3</ac:parameter><ac:parameter ac:name="minLevel">2</ac:parameter></ac:structured-macro></p></ac:layout-cell></ac:layout-section>
                    {p3}
                    <ac:layout-section ac:type="single"><ac:layout-cell><h2>OA基本信息</h2>
                    <h3><span style="color: rgb(17,31,44);">案件信息</span></h3>
                    {p2}
                    <p class="auto-cursor-target"><br /></p></ac:layout-cell></ac:layout-section>
                    <ac:layout-section ac:type="two_right_sidebar"><ac:layout-cell><h3>OA过程</h3>
                    {p4}
                    <h3><span style="color: rgb(17,31,44);">本案原始文件</span></h3><p><strong><span style="color: rgb(17,31,44);">上传：递交文件终版+本次审查意见</span></strong></p><p><strong><span style="color: rgb(17,31,44);"><ac:structured-macro ac:name="attachments" ac:schema-version="1" ac:macro-id="2f5e7a30-9c2b-4b38-b428-02d156dea0c8"><ac:parameter ac:name="old">false</ac:parameter><ac:parameter ac:name="sortOrder">descending</ac:parameter><ac:parameter ac:name="sortBy">createddate</ac:parameter></ac:structured-macro></span></strong></p></ac:layout-cell><ac:layout-cell><strong>子页面（含程序生成的审查意见链接）</strong><p><ac:structured-macro ac:name="children" ac:schema-version="2" ac:macro-id="59998af5-dd35-4f14-b1bc-5135ed771663" /></p></ac:layout-cell></ac:layout-section>
                    <ac:layout-section ac:type="single"><ac:layout-cell><h2>OA1答复策略</h2><ac:structured-macro ac:name="expand" ac:schema-version="1" ac:macro-id="7fa311dc-a2ae-492b-b321-aea0332cb9c2"><ac:rich-text-body><p><br /></p></ac:rich-text-body></ac:structured-macro><p class="auto-cursor-target"><br /></p></ac:layout-cell></ac:layout-section>
                    <ac:layout-section ac:type="single"><ac:layout-cell><h2 class="auto-cursor-target">OA2答复策略</h2><ac:structured-macro ac:name="expand" ac:schema-version="1" ac:macro-id="b298013e-3878-4c8b-8424-b73fcbb12630"><ac:rich-text-body><p><br /></p></ac:rich-text-body></ac:structured-macro><p class="auto-cursor-target"><br /></p></ac:layout-cell></ac:layout-section>
                    <ac:layout-section ac:type="single"><ac:layout-cell><h2 class="auto-cursor-target">US项目CIP或续案建议</h2><ac:structured-macro ac:name="expand" ac:schema-version="1" ac:macro-id="b298013e-3878-4c8b-8424-b73fdbb12630"><ac:rich-text-body><p><br /></p></ac:rich-text-body></ac:structured-macro><p class="auto-cursor-target"><br /></p></ac:layout-cell></ac:layout-section>
                    </ac:layout>
                    """
                    con = TempletWiki
                    isexist = self.getContentByTitleres(fintitle)
                    #判断该页面是否已经存在
                    if isexist:
                        #存在即更新
                        # if customer[0] in ['20849', '20769', '20228', '20229', '20231', '20235', '20236', '20239',
                        #                    '20245', '20252', '20254', '20256', '20257','90009','20901'] or project[0:1] in ['5', '6']:
                        #     for i in isexist:
                        #         if i['space']['key'] == wikikey["key"]:
                        #             con_old = self.getContentById(i['id'])
                        #             re_con = re.search('<th colspan="1"><p><strong>同族人员</strong></p></th><td.*?</td>', con_old, re.DOTALL)
                        #             if re_con:
                        #                 con_new = con_old.replace(re_con.group(), f"""<th colspan="1"><p><strong>同族人员</strong></p></th><td>{tzu_Wcon}</td>""")
                        #                 self.updatePage(i['id'], i['title'], con_new, wikikey["key"])
                        #             break
                        #     return {"code":0,"msg":"OA页面创建成功","url":f"http://10.10.70.90:9090/display/{keyresult}/{fintitle}"}
                        return {"code":0,"msg":"OA页面已存在","url":f"http://10.10.70.90:9090/display/{keyresult}/{fintitle}"}
                    else:
                        self.createChildNewPage(fintitle, con, wikikey["key"], wikpid)
                        return {"code": 0, "msg": "OA页面创建成功","url": f"http://10.10.70.90:9090/display/{keyresult}/{fintitle}"}
                        # return {"code":1,"msg":"OA页面创建失败"}
        else:
            self.createChildNewPage(zutitle,ZUCON,wikikey["key"],wikikey["pid"])
            return self.getContentByTitle(project)


    def getContentById(self, id):
        """
        :param id:指定文章id
        :return:文章内容
        """

        response = requests.get(
            'http://10.10.70.90:9090/rest/api/content/{}?expand=version,body.storage'.format(id),
            auth=(self.admin, self.pwd),
            headers=self.headers)
        json_content = response.text
        parse_content = json.loads(json_content)
        content = parse_content['body']['storage']['value']  # 指定id下的内容
        return content


    def createChildNewPage(self, title, content,key,pid):
        data = {"type": "page", "ancestors": [{"id":f"{pid}"}], "space": {"key": f"{key}"},
                "body": {"storage": {"representation": "storage"}}}  # id为对应空间下的父页面id
        data['title'] = title
        data['body']['storage']['value'] = content
        data = json.dumps(data)
        # print(data)
        response = requests.post('http://10.10.70.90:9090/rest/api/content/',
                                 auth=(self.admin, self.pwd),
                                 headers=self.headers,
                                 data=data
                                 )
        return response.status_code

    def findprojectinfo(self,project):
        connection = pymssql.connect("10.10.70.88", "ipeasy", "!@#123.", "IPEasy", charset='utf8')
        cur = connection.cursor()
        cur.execute(f"select case_name,pub_no from p_case_info where case_volume='{project}'")
        pdetail = cur.fetchone()
        if pdetail:
            ptitle = pdetail[0]
            public = pdetail[1]
        else:
            ptitle = ''
            public = ''
        cur.close()
        connection.close()
        return ptitle,public

    def updatePage(self,cid,title,con,key):
        """
        :param cid:页面id
        :param title: 子页面标题
        :return:
        """
        # version--每更新一次，次数需加一次,若移动到另外父页面，则读取需要被移到的页面的版本+1
        data = {"type": "page", "space": {"key": key}, "body": {"storage": {"representation": "storage"}},
                "version": {"number":int(self.getversion(cid))+1}}
        data['id'] = cid
        data['title'] = title
        data['body']['storage']['value'] = con
        data = json.dumps(data)
        response = requests.put('http://10.10.70.90:9090/rest/api/content/{}'.format(cid),
                                headers=self.headers,
                                data=data,
                                auth=(self.admin, self.pwd))
        code = response.status_code
        print('response:',response)


    def getversion(self,id):
        headers = {'content-type': "application/json"}
        response = requests.get(
            'http://10.10.70.90:9090/rest/api/content/{}/history'.format(id),
            auth=(self.admin, self.pwd),
            headers=self.headers)
        json_content = response.text
        parse_content = json.loads(json_content)
        version = parse_content['lastUpdated']['number']
        # print('version:',version)
        return version



    def GetContentByTitle(self,title):
        response = requests.get(
            'http://10.10.70.90:9090/rest/api/content?title={}&start=0&limit=10&expand=space,history,body.storage,metadata.labels'.format(
                title),
            auth=(self.admin, self.pwd),
            headers=self.headers)
        json_content = response.text
        parse_content = json.loads(json_content)
        if parse_content['results']:
            id = parse_content['results'][0]['id']  # 该页面的id
            content = parse_content['results'][0]['body']['storage']['value']  # 指定title下的内容
            return {'code':200,'res':id,'con':content}
        else:
            return {'code':400}

    def putAttachment(self,fileRoute,pageId=None,ptitle=None):
        if ptitle:
            id_dict = self.GetContentByTitle(ptitle)
            if id_dict['code'] == 200:
                pageId = id_dict['res']
            else:
                return {'code':201,'res':'未找到对应wiki页面，请确认该页面是否存在'}
        files = {'file': open(fileRoute, 'rb')}
        print("pageId:",pageId)
        response = requests.post(f'http://10.10.70.90:9090/rest/api/content/{pageId}/child/attachment',
                                 auth=(self.admin, self.pwd),
                                 headers={'X-Atlassian-Token': 'nocheck', },
                                 files=files
                                 )
        print("response:===",response)
        return {'code':200}



# if __name__ == '__main__':
#     project = '90009-0010IL01'
#     project_title = "project_name"
#     project_wirte = "project_wirte"
#       a = CreateWikiOa().getContentByTitle("90009-0003CN00")
#       print("a:",a)
#     fileRoute = r'D:\metisip\tip-worktime\TIP_performance2\static\pro_assistant\511d661c-1450-11f0-abbe-c563bd9a72b1\附件备份\【OA1-20744-D033CA00】2025-03-31-Office Action.pdf'
#     a = CreateWikiOa().putAttachment(fileRoute,ptitle='90009-0001CN01-OA信息记录表')
#     print(a)