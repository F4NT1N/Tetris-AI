import numpy as np

# --------------------------------------------------------- fonction d'activation -------------------------------------------------------
# sigmoide
def sigmoid(x):
    return 1 / (1 + np.exp(-x))
    
# dérivée de sigmoide pour la rétro-propagation 
def derivative_sigmoid(x):
    return x*(1-x)

# --------------------------------------------------------- fonction de perte ---------------------------------------------------------
# MSE
# y_true représente l'output attendue, et y_predicted est l'output prédit / reçue par le nn
def MSE_loss(y_true, y_predicted):
    return 1/2 * ((y_predicted - y_true) ** 2)

# --------------------------------------------------------- Réseau neuronal -----------------------------------------------------------
class Neural_Network():
    
    # création d'un réseau de neurone avec 1 couche cachée et des poids aléatoires
    def __init__(self, input_size, hidden_size, output_size): 
        self.W1 = np.random.randn(hidden_size, input_size)
        self.B1 = np.zeros(hidden_size)
        self.W2 = np.random.randn(output_size, hidden_size)
        self.B2 = np.zeros(output_size)
    
    def feed_forward(self, inputs):
        inputs = np.array(inputs).reshape(-1,1) # transposer la matrice d'input pour pouvoir la multiplier à la matrice de poids
        print("inputs transposés")
        print(inputs)

        # multiplier la matrice de poids 1 par la matrice d'input transposé et ajouter les biais 1 transposés
        # pour calculer les paramètres d'entrées de la couche cachée.
        Z1 = np.dot(self.W1, inputs) + self.B1.reshape(-1,1) # résultat = matrice de taille (hidden_size / 1)
        print("inputs de la 1ere couche cachée :")
        print(Z1)

        # passer par la fonction d'activation, pour calculer la sortie de la couche cachée
        A1 = sigmoid(Z1) # résultat = matrice de taille (hidden_size / 1)
        print("outputs de la 1ere couche cachée :")
        print(A1)

        # multiplier la matrice de poids 2 par la matrice d'output de la couche précédente en ajoutant les biais 2 transposés
        # pour calculer les paramètres d'entrées de la dernière couche / output couche
        Z2 = np.dot(self.W2, A1) + self.B2.reshape(-1,1) # résultat = matrice de taille (output_size / 1)
        print("inputs de la couche de sortie :")
        print(Z2)

        # passer par la fonction d'activation, pour calculer les outputs du réseau de neurone
        A2 = sigmoid(Z2) # résultat = matrice de taille (output_size / 1)
        print("outputs du réseau de neurone :")
        print(A2)

        # renvoyer les outputs de toutes les couches du réseau pour la rétro propagation
        return A1, A2

    def back_propagation(self, inputs, A1, A2, y_true, learning_rate):
        y_true = np.array(y_true).reshape(-1,1) # transposé la matrice des outputs attendues qu'elle soit semblable à A2
        inputs = np.array(inputs).reshape(1,-1) # transposé la matrice des inputs pour la multiplié à d_Z1 plus tard

        # calculer la perte en utilisant la fonction MSE
        # ce calcul n'est pas utile car il nous suffit simplement de la dérivée de la fonction de perte
        # loss = MSE_loss(y_true, A2)
        # print("perte :")
        # print(loss)
        
        # calcul de la dérivée de la fonction de perte pour connaitre l'erreur à la couche de sortie
        d_loss = (A2 - y_true) # résultat = matrice de taille (output_size / 1)
        print("perte à la couche de sortie :")
        print(d_loss)

        # calcul du gradient de Z2
        # c'est l'erreur à sortie multipliée par la dérivée de la fonction d'activation des outputs A2
        d_Z2 = d_loss * derivative_sigmoid(A2) # résultat = matrice de taille (output_size / 1)
        print("gradient de Z2 :")
        print(d_Z2)

        # calcul des poids W2 en fonction de l'erreur : d_Z2 * A1T = (output_size / 1) * (1 / hidden_size)
        d_W2 = np.dot(d_Z2, A1.T) # resultat = matrice (output_size / hidden_size)
        print("gradient des poids W2 :")
        print(d_W2)

        # calcul des biais b2 en fonction de l'erreur
        d_b2 = d_Z2

        # calcul pour connaitre l'erreur à la sortie de la couche 1
        # c'est la transposé des poids suivants multipliée par l'erreur transmise de la couche suivante
        # W2 * d_Z2 = (output_size / hidden_size) * (output_size / 1)
        d_loss_hidden = np.dot(self.W2.T, d_Z2) # resultat = matrice (output_size / 1)
        print("perte à la sortie de la couche 1 / couche cachée :")
        print(d_loss)

        # calcul du gradient de Z1
        # c'est l'erreur à la sortie de la couche 1 multipliée par la dérivée de la fonction d'activation des outputs A1 de la couche 
        d_Z1 = d_loss_hidden * derivative_sigmoid(A1) # résultat = matrice (hidden_layer / 1)
        print("gradient de Z1 :")
        print(d_Z1)

        # calcul des poids W1 et des biais b1 en fonction de l'erreur
        # la couche précédente étant les inputs Al-1 = inputs, l représente la couche actuelle ici 1
        d_W1 = np.dot(d_Z1, inputs) # résultat = matrice (hidden_size / input_size)
        print("gradient des poids W1 :")
        print(d_W1)
        d_b1 = d_Z1

        # modifié maintenant les poids et les biais en utilisant le taux d'apprentissage:
        self.W1 = self.W1 + learning_rate*d_W1
        self.B1 = self.B1 + learning_rate*d_b1.T
        self.W2 = self.W2 + learning_rate*d_W2
        self.B2 = self.B2 + learning_rate*d_b2.T

""" Note:
matrice de taille 2/1
(x)
(y)
"""


inputs = np.array([1, 1, 3, 4])  # Divise par le maximum ou utilise MinMaxScaler.
y_true = np.array([-1, -1, -3, -4])

learning_rate = 0.1

nn = Neural_Network(4,6,4)
print("poids 1 :")
print(nn.W1)
print("biais 1 :")
print(nn.B1)
print("poids 2 :")
print(nn.W2)
print("biais 2 :")
print(nn.B2)

hidden_outputs, outputs = nn.feed_forward(inputs)

nn.back_propagation(inputs, hidden_outputs, outputs, y_true, learning_rate)

print("nouveau poids 1 :")
print(nn.W1)
print("nouveau biais 1 :")
print(nn.B1)
print("nouveau poids 2 :")
print(nn.W2)
print("nouveau biais 2 :")
print(nn.B2)

nn.feed_forward(inputs)