def clean_weight(value):
    if isinstance(value, str):  # Se for string
        value = value.replace('kg', '').replace('Kg', '').replace('KG', '').strip()  # Remove 'kg'
        value = value.replace(',', '.')  # Troca vírgula por ponto
        try:
            return float(value)  # Tenta converter para float
        except ValueError:
            return None  # Retorna None se a conversão falhar
    elif isinstance(value, (int, float)):  # Se já for numérico
        return float(value)  # Retorna como float
    else:
        return None  # Para outros tipos (e.g., None)

def clean_height(value):
    if isinstance(value, str):  # Se for string
        value = value.replace('cm', '').replace('m', '').replace(',', '.').strip()  # Remove 'cm' e 'm', troca vírgula por ponto
        try:
            return float(value)  # Tenta converter para float
        except ValueError:
            return None  # Retorna None se a conversão falhar
    elif isinstance(value, (int, float)):  # Se já for numérico
        if isinstance(value, int) and value > 100:  # Se for inteiro e maior que 100
            return value / 100.0  # Divide por 100
        return float(value)  # Retorna como float
    else:
        return None  # Para outros tipos (e.g., None)

def check_compulsion(row):
    similar_questions = ['#2','#5', '#8', '#9','#10','#11','#12','#14','#15',]
    similar_answers = {1:0, 2:1, 3:2, 4:3}
    other_questions = {
        '#1': {1:0, 2:0, 3:1, 4:3},
        '#3': {1:0, 2:1, 3:3, 4:3},
        '#4': {1:0, 2:0, 3:0, 4:2},
        '#6': {1:0, 2:1, 3:3, 4:None},
        '#7': {1:0, 2:2, 3:3, 4:3},
        '#13': {1:0, 2:0, 3:2, 4:3},
        '#16': {1:0, 2:1, 3:2, 4:None},
    }
    total = 0
    answers_profile = []
    for column in row.columns:
        if column in similar_questions:
            user_answer = int(row[column].values[0])
            value = similar_answers[user_answer]
        else:
            user_answer = int(row[column].values[0])
            value = other_questions[column][user_answer]
        answers_profile.append([column, user_answer, value])
        total += value
    return total, answers_profile

def check_ortorexia(row):
    similar_questions_01 = ['2','5','8','9']
    similar_answers_01 = {'Sempre': 4, 'Muitas vezes': 3, 'Algumas vezes': 2, 'Nunca': 1}

    similar_questions_02 = ['3','4','6','7','10','11','12','14','15',]
    similar_answers_02 = {'Sempre': 1, 'Muitas vezes': 2, 'Algumas vezes': 3, 'Nunca': 4}

    similar_questions_03 = ['1','13']
    similar_answers_03 = {'Sempre': 2, 'Muitas vezes': 4, 'Algumas vezes': 3, 'Nunca': 1}

    total = 0
    for column in row.columns:
        if column in similar_questions_01:
            user_answer = row[column].values[0]
            value = similar_answers_01[user_answer] 
        elif column in similar_questions_02:
            user_answer = row[column].values[0]
            value = similar_answers_02[user_answer] 
        elif column in similar_questions_03:
            user_answer = row[column].values[0]
            value = similar_answers_03[user_answer]
        total += value
    return total

def check_nutrition_status(peso, altura):
    nutrition_status_cases = {
        'Baixo peso': 1,
        'Peso normal': 2,
        'Sobrepeso': 3,
        'Obesidade grau I': 4,
        'Obesidade grau II': 5,
        'Obesidade grau III': 6,
    }

    imc = peso/(altura)**2
    nutrition_status = ""
    if imc < 18.5:
       nutrition_status =  'Baixo peso'
    elif imc >= 18.5 and imc < 25:
       nutrition_status =  'Peso normal' 
    elif imc >= 25 and imc < 30:
        nutrition_status =  'Sobrepeso'
    elif imc >= 30 and imc < 35:
        nutrition_status =  'Obesidade grau I'
    elif imc >= 35 and imc < 40:
        nutrition_status = 'Obesidade grau II'
    elif imc >= 40:
        nutrition_status =  'Obesidade grau III'
    return nutrition_status, nutrition_status_cases[nutrition_status]