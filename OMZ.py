import requests
import pandas as pd
from datetime import datetime
import time
import re
import json
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import csv
import os

class MetagenomicsLiteratureSearcher:
    def __init__(self):
        self.email = "1130103220@qq.com"  # 替换为你的邮箱
        self.results = []
        self.cache_dir = "search_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # 自定义用户代理
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Connection': 'keep-alive'
        }
        
    def save_cache(self, filename, data):
        """保存缓存数据"""
        with open(os.path.join(self.cache_dir, filename), 'w') as f:
            if isinstance(data, (dict, list)):
                json.dump(data, f)
            else:
                f.write(data)
                
    def load_cache(self, filename):
        """加载缓存数据"""
        try:
            with open(os.path.join(self.cache_dir, filename), 'r') as f:
                if filename.endswith('.json'):
                    return json.load(f)
                else:
                    return f.read()
        except FileNotFoundError:
            return None
    
    def search_literature(self, keyword, max_results=100, source="openalex"):
        """使用多种数据源搜索文献"""
        cache_name = f"{source}_{keyword.replace(' ', '_')}.json"
        cached = self.load_cache(cache_name)
        if cached:
            print(f"使用缓存数据: {cache_name}")
            return cached
            
        results = []
        
        if source == "openalex":
            # 使用OpenAlex API（覆盖PubMed、CrossRef等）
            url = "https://api.openalex.org/works"
            params = {
                "search": keyword,
                "per_page": max_results,
                "mailto": self.email
            }
            try:
                response = requests.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                results = data.get("results", [])
            except Exception as e:
                print(f"OpenAlex搜索失败: {e}")
        
        elif source == "pubmed":
            # PubMed API搜索
            url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            params = {
                "db": "pubmed",
                "term": keyword,
                "retmax": max_results,
                "retmode": "json"
            }
            try:
                response = requests.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                id_list = data.get("esearchresult", {}).get("idlist", [])
                
                # 获取详细文献信息
                fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
                fetch_params = {
                    "db": "pubmed",
                    "id": ",".join(id_list),
                    "retmode": "xml"
                }
                fetch_response = requests.get(fetch_url, params=fetch_params, headers=self.headers)
                fetch_response.raise_for_status()
                
                # 解析XML
                root = ET.fromstring(fetch_response.content)
                for article in root.findall('.//PubmedArticle'):
                    pub = self.parse_pubmed_article(article)
                    if pub:
                        results.append(pub)
            except Exception as e:
                print(f"PubMed搜索失败: {e}")
        
        elif source == "google_scholar":
            # Google Scholar搜索（HTML解析）
            try:
                url = f"https://scholar.google.com/scholar?q={keyword.replace(' ', '+')}"
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                for item in soup.select('.gs_ri'):
                    title_elem = item.select_one('.gs_rt a')
                    if not title_elem:
                        continue
                    
                    title = title_elem.text
                    url = title_elem['href']
                    
                    authors_elem = item.select_one('.gs_a')
                    authors = authors_elem.text if authors_elem else ""
                    
                    # 尝试获取摘要
                    abstract_elem = item.select_one('.gs_rs')
                    abstract = abstract_elem.text if abstract_elem else ""
                    
                    # 尝试获取年份
                    year_match = re.search(r'(\d{4})', authors)
                    year = year_match.group(1) if year_match else ""
                    
                    results.append({
                        "title": title,
                        "authors": authors,
                        "abstract": abstract,
                        "year": year,
                        "url": url,
                        "source": "Google Scholar"
                    })
            except Exception as e:
                print(f"Google Scholar搜索失败: {e}")
        
        # 保存缓存
        if results:
            self.save_cache(cache_name, results)
        
        return results

    def parse_pubmed_article(self, article):
        """解析PubMed文章数据"""
        try:
            medline = article.find('.//MedlineCitation')
            if not medline:
                return None
            
            # 获取文章基本信息
            pmid = medline.findtext('.//PMID')
            title = medline.findtext('.//ArticleTitle')
            abstract = medline.findtext('.//AbstractText') or ""
            
            # 获取作者信息
            authors = []
            for author in medline.findall('.//Author'):
                lastname = author.findtext('LastName')
                forename = author.findtext('ForeName')
                if lastname and forename:
                    authors.append(f"{lastname} {forename}")
                elif lastname:
                    authors.append(lastname)
            
            # 获取期刊信息
            journal = medline.find('.//Journal')
            journal_title = journal.findtext('.//Title')
            journal_date = journal.find('.//JournalDate')
            year = journal_date.findtext('Year') if journal_date else ""
            
            # 获取DOI
            article_id = medline.find('.//ArticleId[@IdType="doi"]')
            doi = article_id.text if article_id is not None else ""
            
            return {
                "id": pmid,
                "title": title,
                "authors": "; ".join(authors),
                "abstract": abstract,
                "journal": journal_title,
                "year": year,
                "doi": doi,
                "source": "PubMed"
            }
        except Exception as e:
            print(f"PubMed解析错误: {e}")
            return None

    def extract_accession_numbers(self, text):
        """从文本中提取可能的序列编号"""
        if not text:
            return []
        
        # 扩展匹配模式
        patterns = [
            r'\bPRJ[EDN][A-Z]?\d+\b',     # BioProject: PRJNA12345
            r'\bPRJEB\d+\b',              # ENA项目: PRJEB12345
            r'\bSR[XPZRS]\d+\b',          # SRA: SRX12345
            r'\bERS\d+\b',                # ERS12345
            r'\bSAM[END]?[A-Z]?\d+\b',    # SRA样本: SAMN12345
            r'\bGSE\d+\b',                # GEO: GSE12345
            r'\bERP\d+\b',                # ENA项目: ERP12345
            r'\bMGYS\d+\b',               # MGnify: MGYS00012345
            r'\bSRR\d+\b',                # SRA运行: SRR12345
            r'\bDRR\d+\b',                # DRA运行: DRR12345
            r'\bERX\d+\b',                # ENA实验: ERX12345
            r'\bMGNIFY:\w+\/\d+\b',      # MGnify项目: MGYA00000000
            r'\b[A-Z]{1,2}\d{5,10}\b'    # 通用格式
        ]
        
        accessions = []
        for pattern in patterns:
            matches = re.findall(pattern, text.upper())
            # 过滤掉一些常见的误匹配
            accessions.extend([m for m in matches if not m.startswith('HTTP') and not m.startswith('WWW')])
        
        return list(set(accessions))

    def check_data_availability(self, accession):
        """检查多个数据库中是否有公开序列数据"""
        # 首先尝试ENA
        ena_result = self.check_ena_data(accession)
        if ena_result:
            return ena_result
        
        # 然后尝试NCBI SRA
        sra_result = self.check_ncbi_sra(accession)
        if sra_result:
            return sra_result
        
        # 最后尝试MGnify
        mgnify_result = self.check_mgnify_data(accession)
        if mgnify_result:
            return mgnify_result
            
        return None

    def check_ena_data(self, accession):
        """检查ENA数据库中的数据"""
        url = "https://www.ebi.ac.uk/ena/portal/api/filereport"
        params = {
            "accession": accession,
            "result": "read_run",
            "fields": "run_accession,scientific_name,base_count,read_count",
            "format": "json"
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                if data and isinstance(data, list) and len(data) > 0:
                    return {
                        "database": "ENA",
                        "accession": data[0].get("run_accession", accession),
                        "scientific_name": data[0].get("scientific_name", ""),
                        "base_count": int(data[0].get("base_count", 0)),
                        "read_count": int(data[0].get("read_count", 0)),
                        "data_url": f"https://www.ebi.ac.uk/ena/browser/view/{accession}"
                    }
        except Exception as e:
            pass
        
        return None

    def check_ncbi_sra(self, accession):
        """检查NCBI SRA数据库中的数据"""
        url = f"https://trace.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?save=efetch&db=sra&rettype=runinfo&term={accession}"
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200 and response.text.strip():
                # 解析CSV格式的响应
                csv_data = list(csv.reader(response.text.strip().split('\n')))
                if len(csv_data) > 1:  # 有数据行
                    headers = csv_data[0]
                    data_row = csv_data[1]
                    
                    # 查找关键字段
                    run_idx = headers.index("Run") if "Run" in headers else 0
                    organism_idx = headers.index("ScientificName") if "ScientificName" in headers else headers.index("Organism") if "Organism" in headers else 1
                    bases_idx = headers.index("Bases") if "Bases" in headers else 2
                    
                    return {
                        "database": "NCBI SRA",
                        "accession": data_row[run_idx],
                        "scientific_name": data_row[organism_idx],
                        "base_count": int(data_row[bases_idx]) if bases_idx < len(data_row) else 0,
                        "read_count": 0,
                        "data_url": f"https://www.ncbi.nlm.nih.gov/sra/{accession}"
                    }
        except Exception as e:
            pass
            
        return None

    def check_mgnify_data(self, accession):
        """检查MGnify数据库中的数据"""
        # 首先尝试项目访问
        project_url = f"https://www.ebi.ac.uk/metagenomics/api/v1/studies/{accession}"
        try:
            response = requests.get(project_url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                if "data" in data and "attributes" in data["data"]:
                    attrs = data["data"]["attributes"]
                    return {
                        "database": "MGnify",
                        "accession": accession,
                        "scientific_name": attrs.get("study-name", ""),
                        "base_count": 0,
                        "read_count": 0,
                        "data_url": f"https://www.ebi.ac.uk/metagenomics/studies/{accession}"
                    }
        except Exception as e:
            pass
        
        # 然后尝试样本访问
        sample_url = f"https://www.ebi.ac.uk/metagenomics/api/v1/samples/{accession}"
        try:
            response = requests.get(sample_url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                if "data" in data and "attributes" in data["data"]:
                    attrs = data["data"]["attributes"]
                    return {
                        "database": "MGnify",
                        "accession": accession,
                        "scientific_name": attrs.get("sample-name", ""),
                        "base_count": 0,
                        "read_count": 0,
                        "data_url": f"https://www.ebi.ac.uk/metagenomics/samples/{accession}"
                    }
        except Exception as e:
            pass
        
        return None

    def process_publication(self, pub):
        """处理单个出版物"""
        pub_id = pub.get("id", pub.get("doi", "") or pub.get("url", ""))
        title = pub.get("title", "")
        authors = pub.get("authors", "")
        journal = pub.get("journal", pub.get("source", ""))
        pub_date = pub.get("year", pub.get("publication_date", ""))
        abstract = pub.get("abstract", "")
        doi = pub.get("doi", "")
        source = pub.get("source", "")
        
        print(f"\n处理文献: {title} ({pub_date})")
        
        # 提取可能的序列编号（从标题+摘要）
        search_text = f"{title}. {abstract}"
        accessions = self.extract_accession_numbers(search_text)
        
        valid_datasets = []
        
        for accession in accessions[:10]:  # 限制每个文献处理的最大编号数
            print(f"  检查编号: {accession}")
            dataset_info = self.check_data_availability(accession)
            
            if dataset_info:
                valid_datasets.append(dataset_info)
                print(f"    ✓ 找到公开序列数据 ({dataset_info['database']}): {dataset_info['scientific_name']}")
            else:
                print(f"    ✗ 未找到公开序列数据")
        
        return {
            "pub_id": pub_id,
            "title": title,
            "authors": authors,
            "journal": journal,
            "year": pub_date,
            "doi": doi,
            "abstract": abstract,
            "source": source,
            "datasets": valid_datasets
        }

    def search_omz_metagenomics(self, keywords=None, max_results_per_source=50):
        """执行OMZ宏基因组文献搜索"""
        if keywords is None:
            keywords = [
                "OMZ metagenomics",
                "oxygen minimum zone metagenome",
                "marine anoxic metagenome",
                "marine oxygen deficient metagenome",
                "anaerobic marine metagenome",
                "suboxic marine metagenome",
                "marine redoxcline metagenome",
                "OMZ microbial community",
                "hypoxic marine metagenome",
                "marine dead zone metagenome",
                "denitrifying marine metagenome",
                "anammox marine metagenome",
                "microbial nitrogen cycle metagenome",
                "sulfur cycle metagenome",
                "oxygen-deficient marine sediment"
            ]
        
        all_publications = []
        
        # 从多个来源搜索
        sources = ["openalex", "pubmed", "google_scholar"]
        
        for keyword in keywords:
            print(f"\n搜索关键词: '{keyword}'")
            
            for source in sources:
                publications = self.search_literature(keyword, max_results_per_source, source)
                
                if publications:
                    print(f"  从 {source} 找到 {len(publications)} 篇相关文献")
                    all_publications.extend(publications)
                else:
                    print(f"  在 {source} 未找到包含关键词 '{keyword}' 的文献")
        
        # 去重
        unique_publications = {pub['title']: pub for pub in all_publications if 'title' in pub}.values()
        print(f"\n找到 {len(unique_publications)} 篇唯一文献")
        
        # 处理每篇文献
        for pub in unique_publications:
            result = self.process_publication(pub)
            if result["datasets"]:
                self.results.append(result)
                time.sleep(0.5)  # 礼貌性延迟
    
    def export_results(self, format="excel"):
        """导出结果到文件"""
        if not self.results:
            print("未找到结果")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 创建扁平化数据用于导出
        export_data = []
        for pub in self.results:
            for dataset in pub["datasets"]:
                export_data.append({
                    "Publication ID": pub["pub_id"],
                    "Title": pub["title"],
                    "Authors": pub["authors"],
                    "Journal": pub["journal"],
                    "Year": pub["year"],
                    "DOI": pub["doi"],
                    "Source": pub["source"],
                    "Accession": dataset<think>