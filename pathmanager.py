import json
import os


class PathManager:
    """
    This class makes absolute paths to some files.
    """
    def __init__(self):
        """
        Makes config if it does not exist and loads it.
        """
        path = str(__file__).replace("pathmanager.py", "paths.json")
        try:
            self.loadConfig(path)
        except FileNotFoundError:
            self.makeConfig()
            self.loadConfig(path)

    def getpath(self, file: str) -> str:
        """
        Gets the absolute path of a file by just the filename.
        :param file: the file you want the absolute path from.
        :return: the absolute path of the file.
        """
        return self.__paths[file]

    def loadConfig(self, path):
        """
        Loads in the dict of filenames and absolute paths.
        :param path: The path to the config json file.
        """
        with open(path) as jsonFile:
            self.__paths = json.load(jsonFile)
            jsonFile.close()

    def makeConfig(self):
        """
        Makes the config json file with absolute paths to filenames except python files in this directory.
        :return:
        """
        paths = {}
        base = str(__file__).replace("pathmanager.py", "")
        for (dirpath, dirnames, filenames) in os.walk(base):
            if dirpath != base:
                continue
            for filename in filenames:
                if filename.endswith(".py") or filename == '.gitignore':
                    continue
                paths[str(filename)] = base + str(filename)
        with open("paths.json", "w") as jsonFile:
            json.dump(paths, jsonFile)
            jsonFile.close()

if __name__ == "__main__":
    p = PathManager()
    print(p.getpath("data.db"))
