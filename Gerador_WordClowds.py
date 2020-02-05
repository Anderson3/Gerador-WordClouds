
import sys, os

if hasattr(sys, 'frozen'):
    os.environ['PATH'] = sys._MEIPASS + ";" + os.environ['PATH']

from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QMessageBox, QMessageBox, QFileDialog, QAction, qApp
from PyQt5.QtGui import QPixmap, QIcon, QImage
from PyQt5 import QtWidgets, QtGui, QtCore

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator


screen_info = QtWidgets.QApplication(sys.argv)
screen = screen_info.primaryScreen()
#print('Screen: %s' % screen.name())
size = screen.size()
print('Size: %d x %d' % (size.width(), size.height()))
screen_larg = size.width()
screen_alt = size.height()
screen_info.exit()
if (screen_larg == 1366 and screen_alt == 768):
	screen_res = 'WXGA'
else:
	screen_res = 'HD+'
print(screen_res)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class App(QtWidgets.QMainWindow):
	def __init__(self):
		super().__init__()
		self.load_ui()
		self.load_signals()

	def load_ui(self):
		if screen_res == 'WXGA':
			self.ui = loadUi(resource_path('layout_wordcloud.ui'),self)
		else:
			self.ui = loadUi(resource_path('layout_wordcloud_hd.ui'),self)

		self.setWindowTitle('Gerador de WordClouds')
		#self.widget.setStyleSheet("Background-Color: #ddebff;")
		self.widget.setStyleSheet("Background-Color: white;")

		self.pushButton_3.setIcon(QtGui.QIcon(resource_path('imagens/positivo.png')))
		self.pushButton_3.setIconSize(QtCore.QSize(15,15))
		self.pushButton_4.setIcon(QtGui.QIcon(resource_path('imagens/negativo.png')))
		self.pushButton_4.setIconSize(QtCore.QSize(15,15))
		self.pushButton_6.setIcon(QtGui.QIcon(resource_path('imagens/limpar.png')))
		self.pushButton_6.setIconSize(QtCore.QSize(15,15))

		self.lista_excecoes = []
		self.imagem_mascara = None
		self.wordcloud_gerada = None

		#salvar_acao = QAction('Abrir', self)
		#salvar.setShortcut('Ctrl+S')

		self.actionNovo.setShortcut('Ctrl+N')
		self.actionNovo.setStatusTip('Novo')
		self.actionAbrir.setShortcut('Ctrl+O')
		self.actionAbrir.setStatusTip('Abrir')
		self.actionSalvar.setShortcut('Ctrl+S')
		self.actionSalvar.setStatusTip('Salvar')
		self.actionSair.setShortcut('Ctrl+Q')
		self.actionSair.setStatusTip('Sair')

		'''----------------------------------------------------------------- FUNCIONAMENTO DE GIFS
		#self.status_txt = QtGui.QLabel()
		movie = QtGui.QMovie("imagens/esquilo.gif")
		#self.status_txt.setMovie(movie)
		self.label_10.setMovie(movie)
		#self.status_txt.setLayout(QtGui.QHBoxLayout())
		#self.status_txt.layout().addWidget(QLabel('Loading...'))
		#self.label_10.layout().addWidget(QLabel('Loading...'))
		movie.start()
		'''
		

		self.setWindowIcon(QtGui.QIcon(resource_path('imagens/icone.ico')))
		self.setFixedSize(490,535)
		self.show()

	def load_signals(self):

		self.pushButton.clicked.connect(self.gerar_wordcloud)
		self.pushButton_2.clicked.connect(self.limpar)
		self.pushButton_3.clicked.connect(self.adicionar_excecao)
		self.pushButton_4.clicked.connect(self.retirar_excecao)
		self.pushButton_6.clicked.connect(self.limpar_excecao)

		self.pushButton_5.clicked.connect(self.mostrar_imagem_mascara)

		self.toolButton.clicked.connect(self.abrir_arquivo_texto)
		self.toolButton_2.clicked.connect(self.abrir_imagem_mascara)

		self.actionNovo.triggered.connect(self.limpar)
		self.actionSalvar.triggered.connect(self.salvar_wordclowd)
		self.actionAbrir.triggered.connect(self.abrir_arquivo_texto)
		self.actionInfos.triggered.connect(lambda:sobre.show())
		self.actionSair.triggered.connect(qApp.quit)


	def definir_arquivo(self, caminho, tipo_arq):
		a = caminho
		b = a.replace('/',' ')
		c = b.split()

		if tipo_arq == 'txt':
			arq = c[-1]
			return arq
		else:
			d = c[-1]
			#d = d.replace('.',' ')
			d = d.split()
			arq = d[0]
			return arq


	def abrir_arquivo_texto(self):
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fileName = QFileDialog.getOpenFileName(self,"Abrir", "","All Files (*);;Text Files (*.txt)", options=options)
		if fileName:
			print(fileName)
		
		#for i in range(len(fileName)):
		#	print(fileName[i])

		try:
			with open(fileName[0], 'r') as f:
				self.textEdit.setText(f.read())

			arq = self.definir_arquivo(fileName[0], 'txt')
			print('Arquivo aberto: ', arq)
			self.label_2.setText(arq)

		except:
			QMessageBox.about(self, "Tipo de Arquivo", "O arquivo selecionado não é do formato de texto simples (\".txt\") ou reconhecível.")
			self.label_2.setText('none')


	def adicionar_excecao(self):
		elemento = self.lineEdit_3.text()
		if elemento != '':
			print('adicionar')
			self.listWidget.addItem(elemento)
			self.lista_excecoes.append(elemento)
			print(self.lista_excecoes)
		else:
			QMessageBox.about(self, "Falta de Palavras", "Insira uma palavra para a lista de excessões da WordCloud")
	def retirar_excecao(self):
		elemento = self.lineEdit_3.text()
		#print('retirar')
		if elemento in self.lista_excecoes:
			for i in self.lista_excecoes:
				if elemento == i:

					indice = self.lista_excecoes.index(i)
					self.listWidget.takeItem(indice)
					self.lista_excecoes.remove(i)

		else:
			print('não existe')
	def limpar_excecao(self):
		for i in range(len(self.lista_excecoes)+1):
			self.listWidget.takeItem(0)
		self.lista_excecoes = []


	def abrir_imagem_mascara(self):
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fileName = QFileDialog.getOpenFileName(self,"Abrir", "","All Files (*);;Portable Network Graphics (*.png);;Joint Photographic Experts Group (*.jpg)", options=options)
		if fileName:
			#print(fileName)

			try:
				imagem_mascara = fileName[0]
				self.imagem_mascara = imagem_mascara

				tipo_imagem_mascara = fileName[1]
				if tipo_imagem_mascara == 'Portable Network Graphics (*.png)':
					self.tipo_imagem_mascara = '.png'
				elif tipo_imagem_mascara == 'Joint Photographic Experts Group (*.jpg)':
					self.tipo_imagem_mascara = '.jpg'
				#self.mascara = np.array(Image.open(imagem_mascara))

				arq = self.definir_arquivo(fileName[0], 'img')
				#arq = str(arq) + str(self.tipo_imagem_mascara)
				print('Máscara: ',arq)

				self.label_9.setText(arq)
			except:
				self.label_9.setText('none')
				self.imagem_mascara = None
				self.tipo_imagem_mascara = None

		#print(imagem_mascara)


	def mostrar_imagem_mascara(self):
		try:
			path = self.imagem_mascara
			if sys.platform == 'linux2':
		  		subprocess.call(["xdg-open", path])
			else:
		  		os.startfile(path)
		except:
  			QMessageBox.about(self, "Falta de Máscara", "Escolha uma imagem para ser a Máscara de filtro para a nuvem de palavras.")


	def gerar_wordcloud(self):
		largura = self.lineEdit.text()
		altura = self.lineEdit_2.text()

		if largura.isdigit() and altura.isdigit():
			
			lista_palavras = self.textEdit.toPlainText()
			largura = int(self.lineEdit.text())
			altura = int(self.lineEdit_2.text())
			cor_fundo = self.comboBox.currentText()
			#mascara = self.mascara
			mascara = None

			if cor_fundo == 'Branco':
				bg_color = 'white'
			elif cor_fundo == 'Preto':
				bg_color = 'black'
			elif cor_fundo == 'Amarelo':
				bg_color = 'yellow'
			elif cor_fundo == 'Azul':
				bg_color = 'blue'
			elif cor_fundo == 'Vermelho':
				bg_color = 'red'
			elif cor_fundo == 'Verde':
				bg_color = 'green'
			elif cor_fundo == 'Laranja':
				bg_color = 'orange'
			elif cor_fundo == 'Roxo':
				bg_color = 'purple'
			elif cor_fundo == 'Rosa':
				bg_color = 'pink'
			

			#print(bg_color)

			if lista_palavras != '':
				#lista_palavras = str(open('palavras.txt', 'r').readlines())
				excecoes = set(STOPWORDS)
				#excecoes.update(['ut', 'quit', 'sit'])
				excecoes.update(self.lista_excecoes)

				#mascara = np.array(Image.open('fundo.png'))

				if self.imagem_mascara == None:
					print('mascara não selecionada')

					wordcloud = WordCloud(stopwords=excecoes, 
						background_color=bg_color,
						width=largura,
						height=altura,
						mask=None)
					wordcloud.generate(lista_palavras)

					fig, ax = plt.subplots(figsize=(7,7))
					ax.imshow(wordcloud, interpolation='bilinear')
					plt.axis('off')

					plt.show(wordcloud)

					self.wordcloud_gerada = fig
					wordcloud.to_file('WC.png')

				else:
					print('mascara selecionada')

					try:
						mask = np.array(Image.open(self.imagem_mascara))

						wordcloud = WordCloud(stopwords=excecoes,
							background_color=bg_color,
							mode="RGBA",
							max_words=100000,
							mask=mask)
						wordcloud.generate(lista_palavras)

						image_colors = ImageColorGenerator(mask)
						fig, ax = plt.subplots(figsize=(7,7))
						ax.imshow(wordcloud.recolor(color_func=image_colors), interpolation="bilinear")
						plt.axis('off')

						plt.show(wordcloud)

						self.wordcloud_gerada = fig
						wordcloud.to_file('WC.png')

					except:
						QMessageBox.about(self, "Tipo de Arquivo", "O arquivo selecionado para a máscara não é do formato de imagens (\".jpg\",\".png\") ou de tipo reconhecível.")

			else:
				QMessageBox.about(self, "Falta de Palavras", "Insira palavras para a geração da nuvem de palavras")

			#print(self.imagem_mascara)
			self.label_9.setText('none')
			self.imagem_mascara = None
			self.tipo_imagem_mascara = None


		else:
			QMessageBox.about(self, "Dados inconsistentes", "Insira valores de dimensões consistentes.")


	def limpar(self):
		self.textEdit.setText('')
		self.label_2.setText('none')
		self.label_9.setText('none')
		self.lineEdit_3.setText(' ')
		

	def salvar_wordclowd(self):
		print(self.wordcloud_gerada)
		if self.wordcloud_gerada != None:
			options = QFileDialog.Options()
			options |= QFileDialog.DontUseNativeDialog
			fileName = QFileDialog.getSaveFileName(self,"Salvar", "","Portable Network Graphics (*.png);;Joint Photographic Experts Group (*.jpg)", options=options)
			if fileName:
				print(fileName)

				try:
					tipo_arquivo = fileName[1]
					if tipo_arquivo == 'Portable Network Graphics (*.png)':
						file_type = '.png'
					elif tipo_arquivo == 'Joint Photographic Experts Group (*.jpg)':
						file_type = '.jpg'

					path = fileName[0]+file_type
					imagem = Image.open('WC.png')
					imagem.save(path)
				except:
					pass
		else:
			QMessageBox.about(self, "Nenhuma WordCloud gerada", "Para salvar uma nuvem de palavras gere inicilamnete dê entrada com informações e dados necessários.")



class Sobre(QtWidgets.QMainWindow):
	def __init__(self):
		super().__init__()
		self.load_ui()

	def load_ui(self):
		if screen_res == 'WXGA':
			self.ui = loadUi(resource_path('layout_wordcloud_info.ui'),self)
		else:
			self.ui = loadUi(resource_path('layout_wordcloud_info_hd.ui'),self)
		
		self.widget.setStyleSheet("Background-Color: white;")


		self.label.setToolTip('Essa \'nunvenzinha\' KAWAII foi escolhida pela minha irmã!')
		self.label_4.setText('<a href="https://github.com/Anderson3">https://github.com/Anderson3</a>')
		self.label_4.setOpenExternalLinks(True)

		self.setWindowTitle('Sobre')
		self.setFixedSize(325,330)
		self.setWindowIcon(QtGui.QIcon(resource_path('imagens/icone.ico')))





if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	aplicacao = App()
	sobre = Sobre()
	app.exec_()
	app = QApplication([])
