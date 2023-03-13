import requests
import statistics


def get_history(itemList, qualities=None, locations='Fort sterling, Thetford, Lymhurst, Bridgewatch, Martlock, Caerleon'):

    format = '.json'
    print(itemList)
    payload = {'locations': locations, 'qualities': qualities}
    url = f'https://www.albion-online-data.com/api/v2/stats/History/{itemList}{format}'
    response = requests.get(url, params=payload)
    data = response.json()
    if response.status_code == 200:
        return data
    else:
        print(response.status_code)
        return False

def get_prices(itemList, qualities=None, locations='Fort sterling, Thetford, Lymhurst, Bridgewatch, Martlock, Caerleon'):

    format = '.json'
    print(itemList)
    payload = {'locations': locations, 'qualities': qualities}
    url = f'https://www.albion-online-data.com/api/v2/stats/Prices/{itemList}{format}'
    response = requests.get(url, params=payload)
    data = response.json()
    if response.status_code == 200:
        return data
    else:
        print(response.status_code)
        return False

def get_death_event(player_name, battle_id):
    format = '.json'
    payload = {'take': 5, 'show_death': True, 'show_kills': False, 'show_assists': False,}
    url = f'https://murderledger.com/api/players/{player_name}/events'
    response = requests.get(url, params=payload)
    data = response.json()
    print(response.status_code)
    info = regear_handeling(data, battle_id)
    loadout = loadout_list(info)
    price_list = loadout_prices(loadout)
    print(response.status_code)
    print(price_list)
    print('\n API FINISHED \n')
    return price_list

#Helper functions ------------------------------
def loadout_prices(loadout_list):


    price_list = loadout_list[1]
    gear_list = loadout_list[0]
    item_list = 'TRASH COLLECTOR'

    for i in range(len(price_list)):
        if i == 0:
            item_list = price_list[i]['id']
        else:
            item_list = f"{item_list},{price_list[i]['id']}"
    
    prices = get_prices(item_list)




    median_prices = []

    no_prices_list = []

    check_empty = False

    for i in range(len(price_list)):
        median_prices_temp = []
        for j in range(len(prices)):
            if price_list[i]['id'] == prices[j]['item_id']:
                counter = j

                while (price_list[i]['id'] == prices[counter]['item_id']):

                    if (int(prices[counter]['quality']) == int(price_list[i]['quality'])) and (int(prices[counter]['sell_price_min']) != 0):
                        median_prices_temp.append(prices[counter]['sell_price_min'])

                    counter+=1
                    if counter >= len(prices):
                        check_empty = True
                        break
                #get the median value of prices in the market
                #price = 0
                if len(median_prices_temp) == 0:
                    check_empty = True
                if check_empty == False:
                    price = statistics.median(median_prices_temp)
                    temp = {'slot': gear_list[i]['slot'], 'item': gear_list[i]['id'], 'price': price, 'quality': gear_list[i]['quality'], 'enchant': gear_list[i]['enchant'], 'tier': gear_list[i]['tier'], 'en_name': gear_list[i]['en_name']}
                    median_prices.append(temp)
                    break
                else:
                    no_prices_list.append(gear_list[i])
                    break
    
    string_item_list = 'none'
    if len(no_prices_list) > 0:
        print(no_prices_list)
        for i in range(len(no_prices_list)):
            if i == 0:
                string_item_list = no_prices_list[0]['id']
                print('###############')
                print(string_item_list)
                print('###############')
            else:
                string_item_list = f"{string_item_list},{no_prices_list[i]['id']}"
                print('###############')
                print(string_item_list)
                print('###############')

        print('\n********************\n')
        print('string item list')
        print(string_item_list)
        print('\n********************\n')
        print('No price list')
        print(no_prices_list)
        print('\n********************\n')

        sell_history = get_history(string_item_list)

        temp_list = []

        for k in range(len(no_prices_list)):
            print(k)
            print('&&&&&&&&&&&&&&&&&&&&&&&&&')
            print(no_prices_list)
            print(len(sell_history))
            for l in range(len(sell_history)):
                print(f"{sell_history[l]['item_id']},{no_prices_list[k]['id']}")
                print(f"{sell_history[l]['quality']},{no_prices_list[k]['quality']} ")
                if no_prices_list[k]['quality'] == 0:
                    no_prices_list[k]['quality'] = 1
                if (sell_history[l]['item_id'] == no_prices_list[k]['id']) and (sell_history[l]['quality'] == no_prices_list[k]['quality']):
                    data = sell_history[l]['data']
                    if len(data) > 0:
                        print('made it through')
                        temp_price = data[0]['avg_price']
                        print(temp_price)
                        print('\n********************\n')
                        print(temp_price)
                        print('\n********************\n')
                        temp_list.append(temp_price)
            if len(temp_list) > 0:
                print(temp_list)
                price = statistics.median(temp_list)
                print(price)
                temp_dict = {'slot': no_prices_list[k]['slot'], 'item': no_prices_list[k]['id'], 'price': price, 'quality': no_prices_list[k]['quality'], 'enchant': no_prices_list[k]['enchant'], 'tier': no_prices_list[k]['tier'], 'en_name': no_prices_list[k]['en_name']}
                median_prices.append(temp_dict)
            else:
                if no_prices_list[k]['id'] == 'T5_MOUNT_COUGAR_KEEPER':
                    {'slot': no_prices_list[k]['slot'], 'item': no_prices_list[k]['id'], 'price': 100000, 'quality': no_prices_list[k]['quality'], 'enchant': 1, 'tier': 5, 'en_name': 'swiftclaw'}
                    median_prices.append(temp_dict)

                price = 0
                temp_dict = {'slot': no_prices_list[k]['slot'], 'item': no_prices_list[k]['id'], 'price': price, 'quality': no_prices_list[k]['quality'], 'enchant': no_prices_list[k]['enchant'], 'tier': no_prices_list[k]['tier'], 'en_name': no_prices_list[k]['en_name']}
                median_prices.append(temp_dict)



    print('\n********************\n')
    print(median_prices)
    print('\n********************\n')
    return median_prices



def loadout_list(info):
    loadout_list = []

    item_id_list = []

    main_hand = info['main_hand']
    main_hand['slot'] = 'main_hand'
    loadout_list.append(main_hand)

    off_hand = info['off_hand']
    off_hand['slot'] = 'off_hand'
    loadout_list.append(off_hand)

    head = info['head']
    head['slot'] = 'head'
    loadout_list.append(head)

    body = info['body']
    body['slot'] = 'body'
    loadout_list.append(body)

    shoe = info['shoe']
    shoe['slot'] = 'shoe'
    loadout_list.append(shoe)

    bag = info['bag']
    bag['slot'] = 'bag'
    loadout_list.append(bag)

    cape = info['cape']
    cape['slot'] = 'cape'
    loadout_list.append(cape)

    mount = info['mount']
    mount['slot'] = 'mount'
    loadout_list.append(mount)

    food = info['food']
    food['slot'] = 'food'
    loadout_list.append(food)

    potion = info['potion']
    potion['slot'] = 'potion'
    loadout_list.append(potion)

    for i in range(len(loadout_list)):

        temp = {'id': loadout_list[i]['id'], 'quality': loadout_list[i]['quality']}

        item_id_list.append(temp)


    print('\n$$$$$$$$$$$$$$$$$$$$$$$$$$$\n')
    print('loadout list')
    print('\n$$$$$$$$$$$$$$$$$$$$$$$$$$$\n')
    full_list = []
    full_list.append(loadout_list)
    full_list.append(item_id_list)
    print(loadout_list)
    return full_list


def regear_handeling(data, battle_id):
    #f = open(data, "r", encoding="utf-8")
    #data = json.load(f)
    print(f'regear handling data \n {data}')
    if data == None:
        return False
    elif len(data) < 1:
        return False
    else:
        data = data['events']
        for i in range(len(data)):
            temp = int(data[i]['id'])
            if temp == int(battle_id):
                data = data[i]['victim']
                data = data['loadout']
                print(data)
                return data

        return False
