# mtgsdk examples menu
# requer: pip install mtgsdk

from mtgsdk import Card, Set, Type, Supertype, Subtype

def pausa():
    input("\nPressione ENTER para continuar...")

def busca_por_nome():
    nome = input("Nome da carta: ")
    cards = Card.where(name=nome).all()
    for c in cards:
        print(c.name, "-", c.set, "-", c.language if hasattr(c, "language") else "")
    pausa()

def busca_por_id():
    mid = input("Multiverse ID: ")
    card = Card.find(mid)
    print(card.name, "-", card.set)
    pausa()

def busca_com_filtros():
    s = input("Set code (ex ktk): ")
    subs = input("Subtipos separados por vírgula: ")
    cards = Card.where(set=s).where(subtypes=subs).all()
    for c in cards:
        print(c.name, "-", c.subtypes)
    pausa()

def busca_pagina():
    p = int(input("Página: "))
    ps = int(input("PageSize: "))
    cards = Card.where(page=p).where(pageSize=ps).all()
    for c in cards:
        print(c.name)
    pausa()

def busca_idioma():
    lang = input("Idioma (ex: Portuguese (Brazil)): ")
    cards = Card.where(language=lang).all()
    for c in cards:
        print(c.name, "-", c.language)
    pausa()

def todas_as_cartas():
    cards = Card.all()
    print("Total:", len(cards))
    pausa()

def set_por_code():
    code = input("Set code (ex ktk): ")
    s = Set.find(code)
    print(s.name, "-", s.release_date)
    pausa()

def todos_os_sets():
    sets = Set.all()
    for s in sets:
        print(s.code, "-", s.name)
    pausa()

def filtro_sets():
    n = input("Nome (ex: khans): ")
    sets = Set.where(name=n).all()
    for s in sets:
        print(s.code, "-", s.name)
    pausa()

def todos_os_types():
    t = Type.all()
    for x in t:
        print(x)
    pausa()

def todos_os_subtypes():
    t = Subtype.all()
    for x in t:
        print(x)
    pausa()

def todos_os_supertypes():
    t = Supertype.all()
    for x in t:
        print(x)
    pausa()

menu = {
    "1": ("Buscar carta por nome", busca_por_nome),
    "2": ("Buscar carta por Multiverse ID", busca_por_id),
    "3": ("Buscar carta com filtros (set + subtipos)", busca_com_filtros),
    "4": ("Buscar página específica de cartas", busca_pagina),
    "5": ("Buscar cartas por idioma", busca_idioma),
    "6": ("Listar todas as cartas", todas_as_cartas),
    "7": ("Buscar Set por código", set_por_code),
    "8": ("Listar todos os Sets", todos_os_sets),
    "9": ("Filtrar Sets", filtro_sets),
    "10": ("Listar todos os Types", todos_os_types),
    "11": ("Listar todos os Subtypes", todos_os_subtypes),
    "12": ("Listar todos os Supertypes", todos_os_supertypes),
}

if __name__ == "__main__":
    while True:
        print("\n=== MTGSDK TEST MENU ===")
        for k, v in menu.items():
            print(k, "-", v[0])
        print("0 - Sair")
        op = input("Opção: ")
        if op == "0":
            break
        if op in menu:
            menu[op][1]()
        else:
            print("Opção inválida")