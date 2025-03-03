import os
import shutil

def copy(source, destination):
    print(f"cwd: {os.getcwd()}")

    if not os.path.exists(source):
        print("source does not exist: ", source)
        return False

    if os.path.exists(destination):
        print("destination already exists: ", destination)
        shutil.rmtree(destination)

    print("making new destination: ", destination)
    os.mkdir(destination)

    print("Copying from source: ", source)
    for f in os.listdir(source):
        source_path = os.path.join(source, f)
        dest_path = os.path.join(destination, f)
        print(f"source_path: {source_path} {os.stat(source_path)}")
        print(f"dest_path: {dest_path}")


        if os.path.isfile(source_path):
            print(f"{source_path} is a file")
            print(f"Copied {f} to {shutil.copy(source_path, destination)}")
        elif os.path.isdir(source_path):
            print(f"{source_path} is a directory")
            copy(source_path, dest_path)
        else:
            print(f"Something went wrong while copying {source_path}")





