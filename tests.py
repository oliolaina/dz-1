import pytest
import sys
import unittest
import os
import zipfile
from main import emulator

def test_ls_default(capfd):
    sh = emulator()
    sh.readcmd("ls")
    out, err = capfd.readouterr()
    expect = "Documents\nDownloads\nPictures\n"
    assert (out == expect)

def test_ls_fromdir(capfd):
    sh = emulator()
    sh.curdir = "Downloads"
    sh.readcmd("ls")
    out, err = capfd.readouterr()
    expect = "styles\nСтруктуры и алгоритмы обработки данных_Практическая работа_6.1 (Хеширование) (1).pdf\nСтруктуры и алгоритмы обработки данных_Практическая работа_6.1 (Хеширование).pdf\n"
    assert (out == expect)

def test_ls_witharg(capfd):
    sh = emulator()
    sh.readcmd("ls Documents")
    out, err = capfd.readouterr()
    expect = "Новая папка\nПрактика 5.2 сиаод.docx\nПрактика 5.2 сиаод.pdf\n"
    assert (out == expect)

def test_ls_wrongarg(capfd):
    sh = emulator()
    sh.readcmd("ls go")
    out, err = capfd.readouterr()
    expect = "No such directory: go\n"
    assert (out == expect)

def test_cd_here(capfd):
    sh = emulator()
    sh.curdir = "Pictures"
    sh.readcmd("cd .")
    assert (sh.curdir == "Pictures")

def test_cd_up(capfd):
    sh = emulator()
    sh.curdir = "Documents/Новая папка"
    sh.readcmd("cd ..")
    assert (sh.curdir == "Documents")

def test_cd_dir(capfd):
    sh = emulator()
    sh.curdir = ""
    sh.readcmd("cd Documents")
    assert (sh.curdir == "Documents")

def test_cd_wrong_dir(capfd):
    sh = emulator()
    sh.curdir = ""
    sh.readcmd("cd Music")
    out, err = capfd.readouterr()
    expect = "No such directory: Music\n"
    assert (out == expect)

def test_cp_from_doc_to_root(capfd):
    sh = emulator()
    sh.curdir = ""
    sh.readcmd('cp "Documents/Практика 5.2 сиаод.docx" pract.docx')
    sh.readcmd('ls')
    out, err = capfd.readouterr()
    expect = "Documents\nDownloads\nPictures\npract.docx\n"
    assert (out == expect)

def test_cp_from_style_to_doc(capfd):
    sh = emulator()
    sh.curdir = ""
    sh.readcmd('cp /Downloads/styles/style.css /Documents')
    sh.readcmd('ls Documents')
    out, err = capfd.readouterr()
    expect = "style.css\nНовая папка\nПрактика 5.2 сиаод.docx\nПрактика 5.2 сиаод.pdf\n"
    assert (out == expect)

def cp_wrong_arg(capfd):
    sh = emulator()
    sh.curdir = ""
    sh.readcmd('cp mylove.png /Downloads')
    out, err = capfd.readouterr()
    expect = "No such file: mylove.png"
    assert (out == expect)


# if __name__ == '__main__':
#     unittest.main()