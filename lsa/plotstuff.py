# -*- coding: utf-8 -*- 

from matplotlib import pylab
import numpy

gscores = numpy.load("scores_500_average.npy")
gaussians = numpy.load("scores_500.npy")
ascores = numpy.load("scores_500_all.npy")

pylab.figure(figsize=(16, 6), dpi=80)

ax1 = pylab.subplot(1,2,1)

ax1.plot(range(210,500,40), gscores)
ax1.set_title(u"Choix de la dimensionalité avec score moyen")
ax1.set_xlabel("Nombre de dimensions des vecteurs de mots")
ax1.set_ylabel("Performance (en %)")
#pylab.savefig("dimensionalite.pdf")

ax2 = pylab.subplot(1,2,2)
ax2.plot(numpy.linspace(2,8,15), gaussians)
ax2.set_title(u"Choix de la variance pour la méthode de score gaussienne")
ax2.set_xlabel("Valeur de la variance")
ax2.set_ylabel("Performance (en %)")

#pylab.show()
pylab.savefig("dimensionalite2.pdf")
