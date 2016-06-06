#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ClientPanel.PanelBaseEx")
#===============================================================================
# 发送指定的字符串ID代替字符串
#===============================================================================
from Game.ClientPanel import PanelBase, PanelTeam



class DialogEx(PanelBase.DialogBase):
	TxtType = 2 #发送指定的字符串ID代替字符串
	
class FilmDialogEx(PanelBase.FilmDialogBase):
	TxtType = 2

class SelectDalogEx(PanelBase.SelectDalogBase):
	TxtType = 2

class TeamFilmDialogEx(PanelTeam.TeamFilmDialog):
	TxtType = 2

