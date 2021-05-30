from pymongo import MongoClient

class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.vacancy300521_2


    def process_item(self, item, spider):
        # Здесь обработка item'a

        if spider.name == 'hhru':
            item['salary'] = self.salary_pipline_hh(item['salary'])
        else:
            item['salary'] = self.salary_pipline_sj(item['salary'])

        collection = self.mongobase[spider.name]
        collection.insert_one(item)

        return item


    def salary_pipline_hh(self, salary):

        min_salary = None
        max_salary = None
        currency = None

        for i in range(len(salary)):
            salary[i] = salary[i].replace(u'\xa0', u'').replace(' ', '')

        if salary[0] == 'до':
            max_salary = int(salary[1])
            currency = salary[-2]
        elif salary[0] == 'от' and len(salary) == 5:
            min_salary = int(salary[1])
            currency = salary[-2]
        elif len(salary) == 7:
            min_salary = int(salary[1])
            max_salary = int(salary[3])
            currency = salary[-2]

        # result = [min_salary, max_salary, currency]
        result = {'min_salary': min_salary, 'max_salary': max_salary, 'currency': currency}
        return result


    def salary_pipline_sj(self, salary):

        min_salary = None
        max_salary = None
        currency = None

        for i in range(len(salary)):
            salary[i] = salary[i].replace(u'\xa0', u' ')
        salary = (' '.join(salary)).split()

        if salary[0] == 'до':
            max_salary = int(salary[1] + salary[2])
            currency = salary[-1]
        elif salary[0] == 'от' :
            min_salary = int(salary[1] + salary[2])
            currency = salary[-1]
        elif len(salary) == 5:
            min_salary = int(salary[0] + salary[1])
            max_salary = int(salary[2] + salary[3])
            currency = salary[-1]

        # result = [min_salary, max_salary, currency]
        result = {'min_salary': min_salary, 'max_salary': max_salary, 'currency': currency}
        return result


