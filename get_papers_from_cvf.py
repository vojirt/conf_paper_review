import requests
import os
from bs4 import BeautifulSoup
import tqdm
import glob
import ntpath
import json

def parse_main_page(url):
    print ("Parsing main conference paige ", url)
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'lxml')

    bib_dict = {}
    dt_id = -1
    for child in tqdm.tqdm(soup.find_all(['dt', 'dd'])):
        if child.name == "dt":
            dt_id += 1
            bib_dict[dt_id] = {}
        if child.name == "dt":
            for tg in [e for e in child.descendants if e.name is not None]:
                if tg.name == "a":
                    bib_dict[dt_id]["title"] = tg.text
                    bib_dict[dt_id]["link_page"] = "http://openaccess.thecvf.com/" + tg.attrs.get("href", "None")
        if child.name == "dd":
            for tg in [e for e in child.descendants if e.name is not None]:
                if tg.name == "a" and tg.text in ["pdf", "supp"]:
                    bib_dict[dt_id]["link_"+tg.text] = "http://openaccess.thecvf.com/" + tg.attrs.get("href", "None")
                if tg.name == "div" and tg.attrs.get("class", "None")[0] == "bibref":
                    bib_dict[dt_id]["bib"] = tg.text
    return bib_dict

def parse_paper_page(bib_dict):
    for key, val in tqdm.tqdm(bib_dict.items()):
        try:
            res = requests.get(val["link_page"])
            res.raise_for_status()
        except Exception as err:
            pass
        else:
            soup = BeautifulSoup(res.content, 'lxml')
            tg = soup.find("div", id="abstract")
            bib_dict[key]["abstract"] = tg.text
            tg = soup.find("div", id="authors")
            for e in tg.recursiveChildGenerator():
                if e.name == "i":
                    bib_dict[key]["authors"] = e.text
                    break
    return bib_dict

def parse_text_title_list(filename):
    bib_dict = {}
    with open(filename, 'r') as fobj:
        titles = fobj.readlines()
        for i in range(0, len(titles)):
            bib_dict[i] = {
                "abstract": "",
                "authors": "",
                "bib": "",
                "link_page": "",
                "link_pdf": "",
                "title": titles[i].replace("\n", "")
            }
    return bib_dict


if __name__ == "__main__":
    out_dir = "./down/"
    titles_only_dir = "./down_titles_only/"
    os.makedirs(out_dir, exist_ok=True)
    conf_list = ["ICCV2021.py", "ICCV2019.py", "ICCV2017.py", "ICCV2015.py", "ICCV2013.py",
                 "CVPR2021.py", "CVPR2020.py", "CVPR2019.py", "CVPR2018.py", "CVPR2017.py", "CVPR2016.py", "CVPR2015.py", "CVPR2014.py", "CVPR2013.py",
                 "ECCV2018.py",
                 "WACV2021","WACV2020.py"]
    for conf in conf_list:
        f = conf.find(".")
        name = conf[:f] if f > 0 else conf
        if not os.path.isfile(out_dir + "/" + name + ".json"):
            bib_dict = parse_main_page("http://openaccess.thecvf.com/" + conf)
            bib_dict = parse_paper_page(bib_dict)
            json.dump(bib_dict, open(out_dir + "/" + name + ".json", 'w'), sort_keys=True, indent=4)
        
    conf_titles_list = sorted([ntpath.basename(fn) for fn in glob.glob(titles_only_dir + "/*.txt")])
    for conf in conf_titles_list:
        if not os.path.isfile(out_dir + "/" + conf[:-4] + ".json"):
            bib_dict = parse_text_title_list(titles_only_dir + "/" + conf)
            json.dump(bib_dict, open(out_dir + "/" + conf[:-4] + ".json", 'w'), sort_keys=True, indent=4)