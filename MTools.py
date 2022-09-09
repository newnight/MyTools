# coding=utf8
import sublime,sublime_plugin,os,json

MTOOLS_PKGNAME = "MyTools"
USER_SETTING_FILE = MTOOLS_PKGNAME+".sublime-settings"
DEFAULT_SETTING_RESOURCE = "Packages/"+MTOOLS_PKGNAME+"/"+USER_SETTING_FILE
USER_CONTEXT_FILE = "Context.sublime-menu"

def create_menu_children():
    children=[]
    for path in s.get('diffList'):
        name = path.get('name')
        target = path.get('path')
        caption = { "caption": name, "command": "difftool_with","args": { "target":target }  }
        length = len(children)
        children.insert(length,caption)
    return children

def create_user_setting():
    user_folder = os.path.join(sublime.packages_path(), 'User')
    user_file = os.path.join(user_folder, USER_SETTING_FILE)
    if os.path.exists(user_file):
        return
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
    user_settings_contents = sublime.load_resource(DEFAULT_SETTING_RESOURCE)
    with open(user_file, 'w', encoding='utf8') as f:
        f.write(user_settings_contents)


def get_default_cmd(type='path'):
    cmd= s.get('defaultDiffTool','bcompare')
    return s.get('diffTools').get(cmd).get(type)


def create_user_menu(overwrite=False):
    global s
    s = sublime.load_settings(MTOOLS_PKGNAME+".sublime-settings")
    user_folder = os.path.join(sublime.packages_path(), 'User', MTOOLS_PKGNAME)
    user_file = os.path.join(user_folder, USER_CONTEXT_FILE)
    if os.path.exists(user_file) and not overwrite:
        return
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
    menu = [{ "caption": "-" },{ "caption": "-" }]
    diffName = get_default_cmd('icon')+"DiffWith"
    caption = { "caption":  diffName,"children":""}
    caption['children']=create_menu_children()
    menu.insert(1,caption)
    menu_contents = json.dumps(menu, sort_keys=True, indent=4, separators=(',', ': '))
    with open(user_file, 'w', encoding='utf8') as f:
        f.write(menu_contents)


class Pref:
    def load(self):
        create_user_menu(overwrite=True)


def plugin_loaded():
    global Pref, s
    s = sublime.load_settings(MTOOLS_PKGNAME+".sublime-settings")
    dir(s)
    Pref = Pref()
    Pref.load()
    create_user_menu()
    create_user_setting()
    s.clear_on_change("reload")
    s.add_on_change("reload", lambda: Pref.load())



class ToolsCommand(sublime_plugin.WindowCommand):
    __first_path=''
    __sec_path=''
    _source=''
    __cmd = ''
    def __init__(self, window):
        super().__init__(window)
        self.is_folder=s.get('level')=='folder'
        self.set_source()
        cmd=get_default_cmd()
        if cmd!='' and os.path.exists(cmd):
            self.__cmd=cmd


    def set_source(self):
        path = self.get_path()
        for source_path in s.get('diffList'):
            name = source_path.get('name')
            source = source_path.get('path')
            if path and (source in path):
                self._source=source


    def get_path(self,is_folder=False):
        path = self.window.active_view().file_name()
        if is_folder and path:
            path=os.path.dirname(path)

        return path

    def runCmd(self,target):
        self.set_source()
        self.__first_path=self.get_path(self.is_folder)
        self.__sec_path=self.__first_path.replace(self._source,target)
        if self._source!=target:
            import subprocess
            subprocess.Popen([self.__cmd,self.__first_path,self.__sec_path])


    def is_visible(self,target=''):
        self.set_source()
        return self.__cmd!='' and self._source!='' and self.get_path()


class DifftoolWithCommand(ToolsCommand):
    def run(self,target):
        self.runCmd(target);

    def is_visible(self,target):
        return super().is_visible() and self._source!=target

