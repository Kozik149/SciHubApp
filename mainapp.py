import models, my_request
import hashlib, random, os, sys, datetime, requests
import xml.etree.ElementTree as ET


class Exercise:
    login = 'your_login'
    password = 'your_password'

    def get_products(self, begin, end):
        list_of_ids = []
        url = "https://scihub.copernicus.eu/dhus/search?q=beginposition:[{}%20TO%20{}]&start={}&rows=100"\
              .format(begin, end, 0)
        get_request = my_request.short_request(url, self.login, self.password)
        tree = ET.fromstring(get_request)
        sum_of_elements = tree.find('{http://a9.com/-/spec/opensearch/1.1/}totalResults').text  # get all elements
        randoms = [random.randrange(0, int(sum_of_elements), 100) for i in range(3)]  # get 3 values
        for x in randoms:
            url = "https://scihub.copernicus.eu/dhus/search?q=beginposition:[{}%20TO%20{}]&start={}&rows=100"\
                  .format(begin, end, x)
            get_request = my_request.short_request(url, self.login, self.password)
            tree = ET.fromstring(get_request)
            length = len(tree.findall('{http://www.w3.org/2005/Atom}entry'))
            random_value = random.randrange(0, length, 1)
            list_of_ids.append(tree.findall('{http://www.w3.org/2005/Atom}entry')[random_value]
                               .find('{http://www.w3.org/2005/Atom}id').text)

        return list_of_ids

    def download(self, id):
        url = "https://scihub.copernicus.eu/dhus/odata/v1/Products('{}')/$value".format(id)  # link for download
        file_path = 'Downloads/{}.zip'.format(id)
        file_name = '{}.zip'.format(id)
        with open(file_path, 'wb') as f:
            response = requests.get(url, stream=True, auth=(self.login, self.password))
            total_length = response.headers.get('content-length')
            print('Downloading {} of lenght {}MB'.format(file_name, round(int(total_length)/1000000, 2)))

            if total_length is None:  # no content length header
                f.write(response.content)
            else:
                dl = 0
                total_length = int(total_length)
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)
                    done = int(50 * dl / total_length)
                    sys.stdout.write('\r[%s%s]' % ('=' * done, ' ' * (50 - done)))
                    sys.stdout.flush()
                print('\n')

    def get_sum(self, id):
        url = "https://scihub.copernicus.eu/dhus/odata/v1/Products('{}')/Checksum/Value/$value".format(id)
        get_request = my_request.short_request(url, self.login, self.password)
        web_sum = get_request.decode('utf-8')
        filepath = 'Downloads/{}.zip'.format(id)
        # md5sum filepath for LINUX
        with open(filepath, 'rb') as fh:
            m = hashlib.md5()
            while True:
                data = fh.read(8192)
                if not data:
                    break
                m.update(data)
            final_sum = m.hexdigest().upper()
        if not web_sum == final_sum:
            raise Exception("Incorrect sums")
        else:
            pass

    def save_as_txt(self, begin, end):
        with open('timerange.txt', 'w') as file:
            file.writelines(begin + '\n')
            file.writelines(end)
            file.close()

    def main_func(self):
        # 2019-06-02T00:00 perfect data
        models.DataBase().delete_all_tasks()
        d1 = datetime.datetime.strptime(sys.argv[1], '%Y-%m-%dT%H:%M')
        d2 = datetime.datetime.strptime(sys.argv[2], '%Y-%m-%dT%H:%M')
        while True:
            if d2 - d1 > datetime.timedelta(days=4):
                print('Data range cant be more than 4 days. Proper format: 2019-05-30T13:22')
                d1 = datetime.datetime.strptime(input(), '%Y-%m-%dT%H:%M')
                d2 = datetime.datetime.strptime(input(), '%Y-%m-%dT%H:%M')
                print(d1)
                print(d2)
            else:
                first = Exercise().get_products('{}.000Z'.format(d1.isoformat()), '{}.000Z'.format(d2.isoformat()))
                print(first)
                # first = Exercise().get_products('2019-01-02T00:00:00.000Z', '2019-01-02T01:00:00.000Z')
                for x in first:
                    self.download(x)
                    self.get_sum(x)
                    path = os.path.abspath("Downloads/{}.zip").format(x)
                    models.DataBase().create_record(x, path, Exercise().get_sum(x))
                models.DataBase().export_to_csv()
                self.save_as_txt(str(d1), str(d2))
                break


if __name__ == '__main__':
    Exercise().main_func()
