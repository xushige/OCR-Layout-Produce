import os
import os.path as osp
import argparse
import glob
import shutil

def main(args):
    test_sets=[]
    with  open(os.path.join(args.dataset_path2, "ImageSets", 'Segmentation',"val.txt"),"r") as f:
            for line in f.readlines():
                    test_sets.append(line.rstrip())
   # import ipdb
   # ipdb.set_trace()
    if not osp.exists(args.output_dir):
        #    print("Output directory already exists:", args.output_dir)
        #  sys.exit(1)
        os.makedirs(args.output_dir)
        os.makedirs(osp.join(args.output_dir, "JPEGImages"))
        os.makedirs(osp.join(args.output_dir, "SegmentationClass"))
        os.makedirs(osp.join(args.output_dir, "SegmentationClassPNG"))
    if not os.path.exists(os.path.join(args.output_dir, "ImageSets")):
        os.mkdir(os.path.join(args.output_dir, "ImageSets"))
        os.mkdir(os.path.join(args.output_dir, "ImageSets", 'Segmentation'))
    jpgs1=glob.glob(osp.join(args.dataset_path1, "JPEGImages","*.jpg"))
    jpgs2=glob.glob(osp.join(args.dataset_path2, "JPEGImages","*.jpg"))
    pngs1=glob.glob(osp.join(args.dataset_path1, "SegmentationClassPNG","*.png"))
    pngs2=glob.glob(osp.join(args.dataset_path2, "SegmentationClassPNG","*.png"))
    jpgs=jpgs1+jpgs2
    pngs=pngs1+pngs2
    with open (os.path.join(args.output_dir, "ImageSets", 'Segmentation',"train.txt"),"w") as f:
        for jpg in jpgs1:
            shutil.copy(jpg,osp.join(args.output_dir, "JPEGImages",osp.basename(jpg)))
            if osp.basename(jpg[:-4]) not in test_sets:
                       f.write(osp.basename(jpg[:-4])+"\n")
            shutil.copy(osp.join(args.dataset_path1, "SegmentationClassPNG", osp.basename(jpg)[:-4]+".png"), osp.join(args.output_dir, "SegmentationClassPNG", osp.basename(jpg)[:-4]+".png"))
        for jpg in jpgs2:
            shutil.copy(jpg,osp.join(args.output_dir, "JPEGImages",osp.basename(jpg)))
            if osp.basename(jpg[:-4]) not in test_sets: 
                f.write(osp.basename(jpg[:-4])+"\n")
            shutil.copy(osp.join(args.dataset_path2, "SegmentationClassPNG", osp.basename(jpg)[:-4]+".png"), osp.join(args.output_dir, "SegmentationClassPNG", osp.basename(jpg)[:-4]+".png"))
    shutil.copy(os.path.join(args.dataset_path2, "ImageSets", 'Segmentation',"val.txt") ,os.path.join(args.output_dir, "ImageSets", 'Segmentation',"val.txt"))
    with open(os.path.join(args.output_dir, "ImageSets", 'Segmentation',"train.txt"),"w") as fw:
       with  open(os.path.join(args.dataset_path1, "ImageSets", 'Segmentation',"train.txt"),"r") as fr1,open(os.path.join(args.dataset_path2, "ImageSets", 'Segmentation',"train.txt"),"r") as fr2:
               for line in fr1.readlines():
                         fw.write(line)
               for line in fr2.readlines():
                         fw.write(line)

 
 


if __name__=="__main__":

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--dataset_path1", help="dataset_path1")
    parser.add_argument("--dataset_path2", help="dataset_path2")
    parser.add_argument("--output_dir", help="output dataset directory")
    # parser.add_argument("--labels", help="labels file", required=True)
    # parser.add_argument(
    #     "--noviz", help="no visualization", action="store_true"
    # )
    args = parser.parse_args()
    print(args.dataset_path1)
    main(args)
