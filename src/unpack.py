import json
import gnu_mo_files as mo
import shutil
import pathlib
import os
import sys
from src.WoWsGameParams import WoWsGameParams
sys.path.append('src')


class WoWsUnpack:
    def __init__(self, path):
        self.path = path

    def _findLatestBinFolder(self):
        """
        Finds the latest folder in the bin folder
        """
        bin_folders = os.listdir("{}/bin".format(self.path))
        if (len(bin_folders) == 0):
            raise ValidationError("Nothing inside bin folder")
        bin_folders.sort()
        return bin_folders[-1]

    def _wowsunpack(self, list: bool = False) -> str:
        latest_bin = self._findLatestBinFolder()
        print("Latest bin folder: " + latest_bin)
        flag = '-l' if list else '-x'
        return 'wowsunpack.exe {} {}/bin/{}/idx -p ../../../res_packages'.format(flag, self.path, latest_bin)

    def writeContentList(self):
        """
        Writes the content list to a file, DEBUG ONLY
        """
        os.system(self._wowsunpack(list=True) + ' > contents.txt')
        print("done writing content list")

    def unpackGameParams(self):
        """
        Unpacks *.data from the bin folder
        """
        os.system(self._wowsunpack() + ' -I content/*.data')
        print("done unpacking game params")

    def decodeGameParams(self):
        """
        Decodes GameParams.data from content folder
        """
        data_path = 'content/GameParams.data'
        if os.path.exists(data_path):
            gp = WoWsGameParams(data_path)
            print("decoding game params")
            gp.decode()
            print("done decoding game params")
        else:
            raise FileNotFoundError("GameParams.data not found")

    def unpackGameIcons(self):
        """
        Unpack game icons from the bin folder
        """
        os.system(self._wowsunpack() + ' -I gui/*.png')
        print("done unpacking game icons")

    def unpackGameMaps(self):
        """
        Unpack game maps from the bin folder
        """
        os.system(self._wowsunpack() + ' -I spaces/*')
        print("done unpacking game icons")

    def decodeLanguages(self):
        """
        Decodes the language from global.mo
        """
        latest_bin = self._findLatestBinFolder()
        language_folder = '{}\\bin\\{}\\res\\texts'.format(
            self.path, latest_bin)

        self._resetDir('langs')
        # only decode en, zh and jp
        for folder in os.listdir(language_folder):
            # if folder in ['en', 'zh', 'ja']:
            decoded_dict = mo.read_mo_file(
                language_folder + '\\' + folder + '\\LC_MESSAGES\\global.mo')
            del decoded_dict['']
            with open('langs/{}_lang.json'.format(folder), 'w', encoding="utf-8") as outfile:
                json_str = json.dumps(decoded_dict, ensure_ascii=False)
                outfile.write(json_str)

        print("done decoding languages")

    def _resetDir(self, dirname: str):
        """
        Removes a directory if it exists and creates a new one.
        """
        if os.path.exists(dirname):
            shutil.rmtree(dirname)
        os.mkdir(dirname)

    def packAppAssets(self):
        """
        Packs assets for WoWs Info
        """
        gui_path = 'gui'
        # TODO: to be updated when finalised
        output_path = '../app/assets'
        self._resetDir(output_path)
        if not os.path.exists(gui_path):
            raise FileNotFoundError("gui folder not found")

        # TODO: code duplication, should be refactored
        # ACHIEVEMENTS
        self._resetDir(output_path + '/achievements')
        for achievement in os.listdir(gui_path + '/achievements/icons'):
            # remove grey icons and two placeholders
            if achievement in ['icon_achievement.png', 'placeholder.png']:
                continue
            if '_des.png' in achievement:
                continue

            formatted_name = achievement.replace(
                'icon_achievement_', ''
            )
            shutil.copy(
                gui_path + '/achievements/icons/' + achievement,
                output_path + '/achievements/' + formatted_name,
            )

        # SHIPS
        self._resetDir(output_path + '/ships')
        for ship in os.listdir(gui_path + '/ship_previews'):
            if ship == 'placeholder.png':
                continue

            shutil.copy(
                gui_path + '/ship_previews/' + ship,
                output_path + '/ships/' + ship,
            )

        # UPGRADES
        self._resetDir(output_path + '/upgrades')
        for modernization in os.listdir(gui_path + '/modernization_icons'):
            formatted_name = modernization.replace(
                'icon_modernization_', ''
            )
            shutil.copy(
                gui_path + '/modernization_icons/' + modernization,
                output_path + '/upgrades/' + formatted_name,
            )

        # FLAGS
        self._resetDir(output_path + '/flags')
        for flag in os.listdir(gui_path + '/signal_flags'):
            if '_des.png' in flag:
                continue
            shutil.copy(
                gui_path + '/signal_flags/' + flag,
                output_path + '/flags/' + flag,
            )

        # CAMOUFLAGES
        self._resetDir(output_path + '/camouflages')
        for camouflage in os.listdir(gui_path + '/camouflages'):
            if not camouflage.startswith('PCEC'):
                continue
            if '_des.png' in camouflage:
                continue
            shutil.copy(
                gui_path + '/camouflages/' + camouflage,
                output_path + '/camouflages/' + camouflage,
            )

        # PERMOFLAGES
        self._resetDir(output_path + '/permoflages')
        for permoflage in os.listdir(gui_path + '/permoflages'):
            if '_des.png' in permoflage:
                continue
            shutil.copy(
                gui_path + '/permoflages/' + permoflage,
                output_path + '/permoflages/' + permoflage,
            )

        # COMMANDER SKILLS
        self._resetDir(output_path + '/skills')
        for skill in os.listdir(gui_path + '/crew_commander/skills'):
            formatted_name = ''.join([x.title() for x in skill.split('_')])
            shutil.copy(
                gui_path + '/crew_commander/skills/' + skill,
                output_path + '/skills/' + formatted_name,
            )

        # CONSUMABLES
        self._resetDir(output_path + '/consumables')
        for consumable in os.listdir(gui_path + '/consumables'):
            if not consumable.startswith('consumable_'):
                continue

            if '_empty.png' in consumable or 'undefined.png' in consumable:
                continue

            formatted_name = consumable.replace('consumable_', '')
            shutil.copy(
                gui_path + '/consumables/' + consumable,
                output_path + '/consumables/' + formatted_name,
            )

        # count the overall size of assets
        root_directory = pathlib.Path(output_path)
        assets_size = sum(
            f.stat().st_size for f in root_directory.glob('**/*') if f.is_file()
        ) / 1024 / 1024
        print("done packing assets, size: {:.2f} MB".format(assets_size))