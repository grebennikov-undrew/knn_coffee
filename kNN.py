import math
import operator 
import pandas as pd
import numpy as np

# Импорт из Excel
def importData(path):
  dataSet = pd.read_excel(path)
  # Переименовать столбцы
  dataSet = dataSet.rename(columns={
        'имя':'name',
        'во сколько встает' : 'wakeUpTime',
        'средний сон' :'AvgSleepHours',
        'работа' :'isWorking',
        'округ' :'region',
        'что родители' : 'parentsDrink',
        'пол' : 'sex',
        'яп' : 'progLang',
        'пьет' : 'factDrink',})
  
  # Нормализация
  dataSet['isWorking'] = dataSet['isWorking']*10
  
  # Нумерация округов
  dataSet['regionNum'] = dataSet.apply(lambda row: 
                        0 if row['region'] == 'ЗАО'
                           else (1 if row['region'] == 'СЗАО'
                           else (2 if row['region'] == 'САО'
                           else (3 if row['region'] == 'СВАО'
                           else (5 if row['region'] == 'ВАО'
                           else (6 if row['region'] == 'ЮВАО'
                           else (7 if row['region'] == 'ЮАО'
                           else (8 if row['region'] == 'ЮЗАО'
                                 else (9 if row['region'] == 'ЦАО' 
                                       else 10) # NAN if no conditions matched
                           )))))))
                       , axis=1)
  # Нумерация напитков
  dataSet['parentsDrinkNum'] = dataSet.apply(lambda row: 
                       5 if row['parentsDrink'] == 'кофе'
                                 else (10 if row['parentsDrink'] == 'чай' 
                                       else 0) # NAN if no conditions matched 
                       , axis=1)

  # Нумерация полов
  dataSet['sexNum'] = dataSet.apply(lambda row: 
                        5 if row['sex'] == 'мужской'
                                 else (10 if row['sex'] == 'женский' 
                                       else 0) # NAN if no conditions matched 
                       , axis=1)
  # Нумерация ЯП
  dataSet['progLangNum'] = dataSet.apply(lambda row: 
                        0 if row['progLang'] == 'питон'
                           else (1 if row['progLang'] == 'свифт'
                           else (2 if row['progLang'] == 'котлин'
                           else (3 if row['progLang'] == 'джава'
                           else (4 if row['progLang'] == 'шарп'
                           else (5 if row['progLang'] == 'с++'
                           else (6 if row['progLang'] == 'дс'
                           else (7 if row['progLang'] == 'луа'
                                 else (8 if row['progLang'] == 'скл' 
                                       else 9) # NAN if no conditions matched
                           )))))))
                       , axis=1)  
  
  return dataSet



# Расчет евклидова расстояния между числовыми значениями
def getDistance(row1, row2, length):
	distance = 0
  # Для каждого поля посчитать дистанцию^2
	for x in range(length):
		distance += pow((row1[x] - row2[x]), 2)
  # Вернуть расстояние (корень) между многомерными величинами
	return math.sqrt(distance)

# Возвращает k наиболее подходящих соседей
def getNeighbors(trainingSet, testRow, k):
  # Все расстояния
	distances = []
  # Количество полей для анализа
	length = len(testRow)-1
  # Для каждого элемента в тестовом наборе вычислить расстояние до рассматриваемой строки
	for x in range(len(trainingSet)):
		distance = getDistance(testRow, trainingSet[x], length)
		distances.append((trainingSet[x], distance))
  # Вычислить k наиболее ближайших соседей
	distances.sort(key=operator.itemgetter(1))
	neighbors = []
	for x in range(k):
		neighbors.append(distances[x][0])
	return neighbors

# Прогноз на основании соседей
def getResponse(neighbors):
	classCount = {}
  # Расчет количества k-соседей в каждом классе
	for x in range(len(neighbors)):
		response = neighbors[x][-1]
		if response in classCount:
			classCount[response] += 1
		else:
			classCount[response] = 1
  # Вывод класса с наибольшим кол-вом k-соседей
	sortedVotes = sorted(classCount.items(), key=operator.itemgetter(1), reverse=True)
	return sortedVotes[0][0]

# Импорт данных из табилцы
dataSet = importData('dataset3.xlsx')

# Процент записей обучающего множества
split = 0.8

trainingSetCount = round(len(dataSet.index) * 0.8)
testSetCount = len(dataSet.index) - trainingSetCount

# Преобразование обучающего множества в массив
trainingSet = pd.DataFrame(dataSet,
                  columns=['wakeUpTime', 'AvgSleepHours', 'isWorking', 'regionNum', 'parentsDrinkNum', 'sexNum', 'progLangNum', 'factDrink']).head(trainingSetCount)
# Преобразование тестового множества в массив
testSet = pd.DataFrame(dataSet,
                  columns=['wakeUpTime', 'AvgSleepHours', 'isWorking', 'regionNum', 'parentsDrinkNum', 'sexNum', 'progLangNum', 'factDrink']).tail(testSetCount)

# Вывод массивов
print ('Train set:')
print (trainingSet)
#print ('Test set:')
#print (testSet)
# Массив результатов
predictions=[]

# К соседей - параметр
k = 3

# Обучение и проверка на тестовом множестве
for x in range(0,len(testSet)):
  neighbors = getNeighbors(trainingSet.to_numpy(), testSet.to_numpy()[x], k)
  result = getResponse(neighbors)
  predictions.append(result)
  #testSet[x]['perdictDrink'] = result
  #print(f'Предсказанное= {result}, Реальное={testSet.to_numpy()[x][-1]}')

testSet = testSet.reset_index()

for x in range(0,len(testSet)):
  testSet.loc[x, 'perdictDrink'] = predictions[x]
print (testSet)