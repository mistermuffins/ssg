import os
import shutil

def rm_children(dir_path):
    for entry in os.listdir(dir_path):
        try:
            path = os.path.join(dir_path, entry)
            print("removing ", path)
            os.remove(path)
        except OSError as e:
            print("entry is a directory: ", e)
            print("running shutil.rmtree on ", path)
            print("platform and implementation provides symlink attack resistent version of rmtree(): ", shutil.rmtree.avoids_symlink_attacks)
            shutil.rmtree(path)
        except FileNotFoundError as e:
          print("file not found: ", e)