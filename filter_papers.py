import json
import glob
import os
import ntpath
import tqdm
import pandas as pd


if __name__ == "__main__":
    down_dir = "./down/"
    out_dir = "./filtered/"
    os.makedirs(out_dir, exist_ok=True)
    
    out_filename = "drivable_robotic.csv"
    keywords = ["drivable", "free", "space", "occupancy", "traversability", "ground", "reaction score", "elevation", "map"]
    ban_keywords = ["latent", "subspace", "sub-space", "kernel", 
    	"coding", "multiclass", "multi-class", "multi-label", 
    	"saliency", "dual", "surface", "scale", "localization", 
        "person", "action" ,"feature", "pedestrian", "inpainting", "lidar", "planning"]
    only_conf = ["ICRA2020", "ICRA2019", "IROS2019"]

    confs = sorted([ntpath.basename(fn)[:-5] for fn in glob.glob(down_dir + "/*.json")])
    save_list = []
    for conf in confs:
        if len(only_conf) > 0 and conf not in only_conf:
            continue

        print ("Filtering conf ", conf)
        bib_dict = json.load(open(down_dir + "/" + conf + ".json", 'r')) 
        for key, val in tqdm.tqdm(bib_dict.items()):
            title = val["title"].lower()
            valid = False
            for word in keywords:
                if title.find(word.lower()) != -1:
                    valid = True
                    break
            for word in ban_keywords:
                if title.find(word.lower()) != -1:
                    valid = False 
                    break
            if valid:
                val["conference"] = conf[:-4]
                val["bib"] = val["bib"].replace("\n", "")
                val["year"] = conf[-4:]
                val["abstract"] = val["abstract"].replace("\n", "").strip()
                save_list.append(val)

    print ("\nNum. matches: ", len(save_list))
    df = pd.DataFrame(save_list, columns =["title", "conference", "year", "authors", "link_pdf", "abstract", "bib"]) 
    print (df.head(20))
    df.to_csv(out_dir + "/" + out_filename)

