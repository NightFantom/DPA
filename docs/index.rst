.. OpenMind documentation master file, created by
   sphinx-quickstart on Tue May  8 08:03:17 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to OpenMind's documentation!
===============================
.. image:: https://readthedocs.org/projects/dpa/badge/?version=latest
   :target: http://dpa.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

Introduction
============

Nowadays Digital Personal Assistants (DPA) become more and more popular. DPAs help to increase quality of life especially for elderly or disabled people. The system is designed to use the DPA as a learning platform for engineers to provide them with the opportunity to create and test their own hypothesis. The DPA is able to recognize users' commands in natural language and transform it to the set of machine commands that can be used to control different 3rd-party application. 

Instaliation
============
1. Install dependency from file instal_dependenses.bat
2. Download project `CoreNLP <https://stanfordnlp.github.io/CoreNLP/>`_
3. Install JDK 1.8 (Required for CoreNLP)
4. Make a copy of file src/configs/default_config.ini in the same folder and name it "config.ini". It allows you to change settings without conflicts with VSC.
5. Download W2V for English and put it in folder data with name "word2vect_300.bin". (Recomended Google News W2V 300)
6. Run CoreNLP
7. Run src/Main.py


Architecture
============
In project 5 moduls can be lighlited:

1. Intent processor application is responsible for handling particular user's intents
2. Language processing module provides API for natural language modules
3. Translation module translates unsupported by the DPA languages into supported one
4. Text similarity module is responsible for measurement of text equality
5. Information extraction module retrieves payload information from text


Papers
======
Open source platform Digital Personal Assistant: `https://arxiv.org/abs/1801.03650 <https://arxiv.org/abs/1801.03650>`_

Messengers
==========

WhatsApp module installation instruction:

1. Clone WhatsApp-framework(forked) : https://github.com/RedMoon32/whatsapp-framework
2. Follow instructions of installations and configuring
3. Add project to sources(if you work in Pycharm), or  add the path to framework using sys.path
   (in interface/__init__.py)
4. Now you can run assistant on WhatsApp platform

Other
=====

The Digital Personal Assistant uses Yandex Translation engine.
