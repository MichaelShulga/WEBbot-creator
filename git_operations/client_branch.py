import json
import shutil
import stat
import uuid
import os
from os import listdir
from subprocess import call

from git import Repo


def delete_git_file(folder):
    # delete .git
    def on_rm_error(func, path, exc_info):
        os.chmod(path, stat.S_IWRITE)
        os.unlink(path)

    for i in os.listdir(folder):
        if i.endswith('git'):
            tmp = os.path.join(folder, i)
            # We want to unhide the .git folder before unlinking it.
            while True:
                call(['attrib', '-H', tmp])
                break
            shutil.rmtree(tmp, onerror=on_rm_error)


def delete_folder(folder):
    # delete permission denied file - .git
    delete_git_file(folder)

    # delete folder
    shutil.rmtree(folder, ignore_errors=True)


class ClientRepo:
    def __init__(self, curr_dir, url):
        self.curr_dir = curr_dir
        self.url = url

        # delete if already exists
        if os.path.isdir(self.curr_dir):
            delete_folder(self.curr_dir)

        # clone repo
        self.repo = Repo.clone_from(url, curr_dir, branch='master')

    def update_client_settings(self):
        folder = 'client_settings'
        path = os.path.join(self.curr_dir, folder)

        shutil.rmtree(folder, ignore_errors=True)
        os.makedirs("client_settings")

        for file in listdir(path):
            shutil.copy(os.path.join(path, file), os.path.join("client_settings", file))

    def update_bot_file(self, bot, bot_path=os.path.join('client_settings', 'bot.py')):
        with open(self.curr_dir + os.path.sep + bot_path, 'wb') as new:
            new.write(bot.read())

    def update_additional_file(self, additional, additional_path=os.path.join('client_settings', 'additional.json')):
        with open(self.curr_dir + os.path.sep + additional_path, 'w') as file:
            json.dump(additional, file, ensure_ascii=False)

    def commit_and_push(self, new_branch):
        status = None
        if self.repo is None:
            status = 'Repo is None'

        current = self.repo.create_head(new_branch)
        current.checkout()
        master = self.repo.heads.master
        self.repo.git.pull('origin', master)

        if not os.path.exists(self.curr_dir):
            os.makedirs(self.curr_dir)

        print('file created---------------------')
        if self.repo.index.diff(None) or self.repo.untracked_files:

            self.repo.git.add(A=True)
            self.repo.git.commit(m='msg')
            self.repo.git.push('--set-upstream', 'origin', current)
            status = 'git push'
        else:
            status = 'no changes'
            new_branch = 'master'
        return f'{self.url}/tree/{new_branch}', status


if __name__ == '__main__':
    # repo init
    repo_name = "CLIENT_REPO"
    main_path = os.path.dirname(os.path.realpath(__file__)).replace('git_operations', '')
    repo_path = os.path.join(main_path, repo_name)
    git_url = 'https://github.com/MichaelShulga/bot-creator-heroku'
    client_repo = ClientRepo(repo_path, git_url)

    # update file of repo
    client_repo.update_additional_file({})

    # commit and push changes
    branch = str(uuid.uuid4())  # branch name
    client_repo.commit_and_push(branch)
    print(branch)
