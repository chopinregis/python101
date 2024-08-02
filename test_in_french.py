print ("hello my name Karen")

def saluer(nom):
    return f"bonjour {nom}, comment vas-tu ?"

print(saluer("Karen"))
print(saluer("Regis"))

def manger(nom_de_fruit, nom_de_la_personne):
    return f"{nom_de_la_personne} aime manger le fruit que on appele la {nom_de_fruit}, parce que c'est une bonne nouriture"

print(manger("banane", "Regis"))
print(manger("tomate", "Karen"))