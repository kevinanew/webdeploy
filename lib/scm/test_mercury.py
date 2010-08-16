# coding: utf-8
import shutil
import os

from mercury import Mercury

current_dir = os.path.dirname(__file__)


def test_package():
    repository_url = os.path.join(current_dir,
        'test_repository/hg_project')
    deploy_dir = os.path.join(current_dir,
        'test_repository/deploy_hg_project/export')

    scm = Mercury(repository_url=repository_url, deploy_dir=deploy_dir)

    scm.package()

    assert scm.get_revision() == 0

    scm.build_revision_file()
    assert os.path.exists('%s/revision.txt' % scm.export_dir) == True

    if os.path.exists(scm.work_dir):
        shutil.rmtree(scm.work_dir)

    if os.path.exists(scm.deploy_dir):
        shutil.rmtree(scm.deploy_dir)
