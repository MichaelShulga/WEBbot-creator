import json
import uuid
from os import path
from git import Repo
import os


main_path = os.path.dirname(path.realpath(__file__)).replace('github_bot_file_commit', '')
curr_dir = path.join(main_path, "CLIENT_REPO")
print(curr_dir)
repo = Repo(curr_dir)


def commit_files(new_branch, bot, additional):
    if repo is None:
        print("None repo")

    current = repo.create_head(new_branch)
    current.checkout()
    master = repo.heads.master
    repo.git.pull('origin', master)

    # creating file
    with open(curr_dir + path.sep + os.path.join('client_settings', 'bot.py'), 'wb') as new:
        new.write(bot.read())

    with open(curr_dir + path.sep + os.path.join('client_settings', 'additional.json'), 'w') as file:
        json.dump(additional, file, ensure_ascii=False)

    if not path.exists(curr_dir):
        os.makedirs(curr_dir)
    print('file created---------------------')

    if repo.index.diff(None) or repo.untracked_files:

        repo.git.add(A=True)
        repo.git.commit(m='msg')
        repo.git.push('--set-upstream', 'origin', current)
        print('git push')
    else:
        print('no changes')


if __name__ == '__main__':
    with open('client_branch.py', 'rb') as f:
        name = str(uuid.uuid4())
        print(name)
        commit_files(name, f, 'test_file.py')
        print(name)
