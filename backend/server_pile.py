import utils
from utils import time
from user_bill import Bill, User
from utils import ReportModel


class Pile:
    def __init__(self, pile_id, mode, pile_status=1):
        self.pile_id = pile_id
        self.mode = mode
        self.status = pile_status
        self.charge_speed = 30 if mode == 0 else 7
        self.total_amount = 0
        self.total_times = 0
        self.total_time = 0
        self.total_fee = 0
        self.service_fee = 0
        self.charge_fee = 0
        self.charge_user = []
    
    def check_and_start(self, t):
        if len(self.charge_user):
            self.charge_user[0].begin_time = t
    
    def calculate_fee(self, user, mode):
        
        return self.charge_speed*(user.end_time-user.begin_time)/3600, (user.end_time-user.begin_time)/60, \
            self.query_charge_fee(self.charge_speed, user.begin_time, user.end_time), \
            self.charge_speed*(user.end_time-user.begin_time)/3600*0.8, \
            self.query_charge_fee(self.charge_speed, user.begin_time, user.end_time)+self.charge_speed*(user.end_time-user.begin_time)/3600*0.8
    
    def end_charging(self, t, finish_type, bill_id):
        # finish_type:0 正常结束 1 强制结束 2 异常结束
        # print('finish_type', finish_type)
        user = self.charge_user[0]
        self.charge_user.pop(0)
        if finish_type == 0:
            user.end_time = user.begin_time + user.cost_time
        else:
            user.end_time = t
        self.check_and_start(user.end_time)
        end_time = user.end_time
        
        amount, cost_time, charge_fee, service_fee, total = self.calculate_fee(user, self.mode)
        
        if finish_type ==0 :
            amount = user.amount
            
        # print(amount, cost_time, charge_fee, service_fee, total)
        
        self.total_time += cost_time
        self.total_amount += amount
        self.charge_fee += charge_fee
        self.service_fee += service_fee
        self.total_fee += total
        self.total_times+=1
        
        new_bill = Bill(bill_id, self.pile_id, user.user_id, t, user.begin_time, user.end_time, amount, cost_time, charge_fee, service_fee, total)
        
        if finish_type == 2:
            # amount = user.amount - amount
            user.amount -= amount
            user.begin_wait= t
            user.begin_time = 0
            user.end_time = 0
        return user, end_time, new_bill
    
    def get_wait_time(self):
        # print(utils.Time().get_time_str(self.charge_user[0].begin_time), '+', sum([user.cost_time for user in self.charge_user[0:]]))
        return sum([user.cost_time for user in self.charge_user[0:]])+self.charge_user[0].begin_time

    def query_charge_fee(self, speed, begin_time, end_time):
        if end_time <= 25200: # 7 * 3600
            return (0.4) * speed * (end_time - begin_time) / 3600
        elif begin_time <= 25200 and end_time >= 25200:
            return (0.4) * speed * (25200 - begin_time) / 3600 + \
                (0.7) * speed * (end_time - 25200) / 3600
        elif begin_time >= 25200 and end_time <= 36000: # 10 * 3600
            return (0.7) * speed * (end_time - begin_time) / 3600
        elif begin_time <= 36000 and end_time >= 36000:
            return (0.7) * speed * (36000 - begin_time) / 3600 + \
                (1.0) * speed * (end_time - 36000) / 3600
        elif begin_time >= 36000 and end_time <= 54000 : # 15 * 3600
            return (1.0) * speed * (end_time - begin_time) / 3600
        elif begin_time <= 54000 and end_time >= 54000:
            return (1.0) * speed * (54000 - begin_time) / 3600 + \
                (0.7) * speed * (end_time - 54000) / 3600
        elif begin_time >= 54000:
            return (0.7) * speed * (end_time - begin_time) / 3600
        else:
            assert 0, f'Time Error: begin_time = {begin_time}, end_time = {end_time}'
        return 0.0
    
class Server:
    def __init__(self, timer, mode = "default"):
        self.timer = timer
        self.pile = []
        self.mode = mode
        self.pile_num = 5
        self.bill_num = 0
        self.queue_number = 0
        self.bill_dict = {}
        self.sep =2
        for i in range(self.pile_num):
            self.pile.append(Pile(i, 0 if i < self.sep else 1))
        self.priority_queue = [[], []]
        self.waiting_queue = [[], []]
        
    def modify_mode(self, user_id, mode, amount):
        for i in range(len(self.waiting_queue)):
            for j in range(len(self.waiting_queue[i])):
                if self.waiting_queue[i][j].user_id == user_id:
                    if amount >0 and mode =='keep':
                        self.waiting_queue[i][j].amount = amount
                    elif amount <0 and mode !='keep':
                        user = self.waiting_queue[i].pop(j)
                        self.queue_number+=1
                        user.queue_number = self.queue_number
                        user.mode = 0 if mode =='fast' else 1
                        self.waiting_queue[user.mode].append(user)
                    return
    def print_stat(self, cur_time):
        waiting_queue_stat = []
        for i in range(len(self.waiting_queue)):
            for j in range(len(self.waiting_queue[i])):
                d = {
                    "user_id" : self.waiting_queue[i][j].user_id,
                    "mode" : self.waiting_queue[i][j].mode,
                    "amount" : self.waiting_queue[i][j].amount
                }
                waiting_queue_stat.append(d)
        piles_queue_stat = []
        for i in range(self.pile_num):
            pile_queue_stat = []
            for j in range(len(self.pile[i].charge_user)):
                amount = self.pile[i].charge_speed*(cur_time-self.pile[i].charge_user[j].begin_time)/3600
                # print(cur_time, self.pile[i].charge_user[j].begin_time)
                fee = self.pile[i].query_charge_fee(self.pile[i].charge_speed, 
                                                    self.pile[i].charge_user[j].begin_time, cur_time) + \
                                                    self.pile[i].charge_speed * \
                                                    (cur_time-self.pile[i].charge_user[j].begin_time)/3600*0.8
                if j > 0:
                    amount = fee = 0
                pile_queue_stat.append({"user_id": self.pile[i].charge_user[j].user_id, 
                                        "amount": amount, 
                                        "fee": fee})
            piles_queue_stat.append(pile_queue_stat)
        return piles_queue_stat, waiting_queue_stat
    def schedule(self):
        if self.mode == 'default':
            finish_time = {}
            while 1 :
                tag = 0
                for pile_id in range(5):
                    ti = self.timer.get_time_sec()
                    if len(self.pile[pile_id].charge_user) and \
                        self.pile[pile_id].charge_user[0].begin_time + self.pile[pile_id].charge_user[0].cost_time <= ti:
                        # print(self.pile[pile_id].charge_user[0].begin_time, self.pile[pile_id].charge_user[0].cost_time, ti)
                        self.bill_num+=1
                        _, t, new_bill = self.pile[pile_id].end_charging(ti, 0,self.bill_num)
                        finish_time[pile_id] = t
                        
                        tag = 1
                        
                        if self.bill_dict.get(new_bill.user_id) == None:
                            self.bill_dict[new_bill.user_id] = [new_bill]
                        else:
                            self.bill_dict[new_bill.user_id].append(new_bill)
                
                while 1:
                    bz = 0
                    for mode in range(2):
                        pile_id = self.find_best_pile(mode)
                        #print('now mode is ', mode, 'best pile_id is ', pile_id)
                        if pile_id == -1:
                            continue
                        if self.priority_queue[mode]:
                            if len(self.pile[pile_id].charge_user) <=2: # and self.priority_queue[mode][0].begin_wait <= t:
                                user = self.priority_queue[mode].pop(0)
                                #print("-----schedule---user_id is ", user.user_id, " mode is ", mode)
                                # check begin
                                user.begin_time = self.timer.get_time_sec() #if len(self.pile[pile_id].charge_user)==0 else self.pile[pile_id].charge_user[-1].begin_time + self.pile[pile_id].charge_user[-1].cost_time
                                # print('-------begin_time is ', user.begin_time)
                                user.cost_time = int(user.amount / (30 if mode == 0 else 7) * 3600)
                                self.pile[pile_id].charge_user.append(user)
                                #print("ADD", user.user_id, pile_id)
                                bz = 1
                        elif self.waiting_queue[mode]:
                            if len(self.pile[pile_id].charge_user) <=2: # and self.waiting_queue[mode][0].begin_wait <= t:
                                user = self.waiting_queue[mode].pop(0)
                                # print("-----schedule---user_id is ", user.user_id, " mode is ", mode)
                                # check begin
                                user.begin_time = self.timer.get_time_sec() #if len(self.pile[pile_id].charge_user)==0 else self.pile[pile_id].charge_user[-1].begin_time + self.pile[pile_id].charge_user[-1].cost_time
                                # print('-------begin_time is ', user.begin_time)
                                user.cost_time = int(user.amount / (30 if mode == 0 else 7) * 3600)
                                self.pile[pile_id].charge_user.append(user)
                                # print("ADD", user.user_id, pile_id)
                                bz = 1
                        # ?
                    if bz==0:
                        break
                if tag == 0:
                    break
        elif self.mode == "4a":
            finish_time = {}
            while 1 :
                tag = 0
                for pile_id in range(5):
                    ti = self.timer.get_time_sec()
                    if len(self.pile[pile_id].charge_user) and \
                        self.pile[pile_id].charge_user[0].begin_time + self.pile[pile_id].charge_user[0].cost_time <= ti:
                        # print(self.pile[pile_id].charge_user[0].begin_time, self.pile[pile_id].charge_user[0].cost_time, ti)
                        self.bill_num+=1
                        _, t, new_bill = self.pile[pile_id].end_charging(ti, 0,self.bill_num)
                        finish_time[pile_id] = t
                        
                        tag = 1
                        
                        if self.bill_dict.get(new_bill.user_id) == None:
                            self.bill_dict[new_bill.user_id] = [new_bill]
                        else:
                            self.bill_dict[new_bill.user_id].append(new_bill)
                
                while 1:
                    bz = 0
                    for mode in range(2):
                        pile_id = self.find_best_pile(mode)
                        if len(self.pile[pile_id].charge_user) > 0:
                            continue
                        # print('now mode is ', mode, 'best pile_id is ', pile_id)
                        if pile_id == -1:
                            continue
                        if self.priority_queue[mode]:
                            if len(self.pile[pile_id].charge_user) <=2: # and self.priority_queue[mode][0].begin_wait <= t:
                                user = self.priority_queue[mode].pop(0)
                                # print("-----schedule---user_id is ", user.user_id, " mode is ", mode)
                                # check begin
                                user.begin_time = self.timer.get_time_sec() #if len(self.pile[pile_id].charge_user)==0 else self.pile[pile_id].charge_user[-1].begin_time + self.pile[pile_id].charge_user[-1].cost_time
                                # print('-------begin_time is ', user.begin_time)
                                user.cost_time = int(user.amount / (30 if mode == 0 else 7) * 3600)
                                self.pile[pile_id].charge_user.append(user)
                                bz = 1
                        elif self.waiting_queue[mode]:
                            if len(self.pile[pile_id].charge_user) <=2: # and self.waiting_queue[mode][0].begin_wait <= t:
                                user = self.waiting_queue[mode].pop(0)
                                # print("-----schedule---user_id is ", user.user_id, " mode is ", mode)
                                # check begin
                                user.begin_time = self.timer.get_time_sec() #if len(self.pile[pile_id].charge_user)==0 else self.pile[pile_id].charge_user[-1].begin_time + self.pile[pile_id].charge_user[-1].cost_time
                                # print('-------begin_time is ', user.begin_time)
                                user.cost_time = int(user.amount / (30 if mode == 0 else 7) * 3600)
                                self.pile[pile_id].charge_user.append(user)
                                bz = 1
                        # ?
                    if bz==0:
                        break
                
                # mode == Fast
                if sum(map(lambda x:len(x.charge_user) == 1, self.pile[:self.sep])) == self.sep:
                    users = self.priority_queue[0][:self.sep]
                    self.priority_queue[0] = self.priority_queue[0][self.sep:]
                    if len(users) < self.sep:
                        rem = self.sep - len(users)
                        users.extend(self.waiting_queue[0][:rem])
                        self.waiting_queue[0] = self.waiting_queue[0][rem:]
                    for u in users:
                        u.begin_time = self.timer.get_time_sec()
                        u.cost_time = int(u.amount / 30 * 3600)
                    print('users is ', users)
                    users.sort(key=lambda x:-x.cost_time)
                    for u in users:
                        pile_id = self.find_best_pile(0)
                        self.pile[pile_id].charge_user.append(u)
                        assert(len(self.pile[pile_id].charge_user) == 2)

                # mode == Slow
                if sum(map(lambda x:len(x.charge_user) == 1, self.pile[self.sep:])) == self.sep:
                    slow_piles = self.pile_num - self.sep
                    users = self.priority_queue[1][:slow_piles]
                    self.priority_queue[1] = self.priority_queue[1][slow_piles:]
                    if len(users) < slow_piles:
                        rem = slow_piles - len(users)
                        users.extend(self.waiting_queue[1][:rem])
                        self.waiting_queue[1] = self.waiting_queue[1][rem:]
                    for u in users:
                        u.begin_time = self.timer.get_time_sec()
                        u.cost_time = int(u.amount / 7 * 3600)
                    print('users is ', users)
                    users.sort(key=lambda x:-x.cost_time)
                    for u in users:
                        pile_id = self.find_best_pile(1)
                        self.pile[pile_id].charge_user.append(u)
                        assert(len(self.pile[pile_id].charge_user) == 2)

                if tag == 0:
                    break
        elif self.mode == "4b":
            finish_time = {}
            while 1 :
                tag = 0
                for pile_id in range(5):
                    ti = self.timer.get_time_sec()
                    if len(self.pile[pile_id].charge_user) and \
                        self.pile[pile_id].charge_user[0].begin_time + self.pile[pile_id].charge_user[0].cost_time <= ti:
                        print(self.pile[pile_id].charge_user[0].begin_time, self.pile[pile_id].charge_user[0].cost_time, ti)
                        self.bill_num+=1
                        _, t, new_bill = self.pile[pile_id].end_charging(ti, 0,self.bill_num)
                        finish_time[pile_id] = t
                        
                        tag = 1
                        
                        if self.bill_dict.get(new_bill.user_id) == None:
                            self.bill_dict[new_bill.user_id] = [new_bill]
                        else:
                            self.bill_dict[new_bill.user_id].append(new_bill)
            
                if all(map(lambda x:len(x.charge_user) == 0, self.pile)) \
                    and len(self.waiting_queue[0]) + len(self.waiting_queue[1]) >= 2 * self.pile_num:
                    total_seats = self.pile_num * 2
                    users = self.waiting_queue[0][:total_seats]
                    self.waiting_queue[0] = self.waiting_queue[0][total_seats:]
                    if len(users) < total_seats:
                        rem = total_seats - len(users)
                        users.extend(self.waiting_queue[1][:rem])
                        self.waiting_queue[1] = self.waiting_queue[1][rem:]
                    users.sort(key=lambda x:-x.amount)
                    print(f'len of users is {len(users)}')
                    fast_users = users[:self.sep*2]
                    for u in fast_users:
                        u.begin_time = self.timer.get_time_sec()
                        u.cost_time = int(u.amount / 30 * 3600)
                    fast_users = list(zip(
                        fast_users[:self.sep],
                        reversed(fast_users[self.sep:])
                    ))
                    slow_users = users[self.sep*2:]
                    slow_piles = self.pile_num - self.sep
                    for u in slow_users:
                        u.begin_time = self.timer.get_time_sec()
                        u.cost_time = int(u.amount / 7 * 3600)
                    slow_users = list(zip(
                        slow_users[:slow_piles],
                        reversed(slow_users[slow_piles:])
                    ))
                    print('fast users is ', fast_users)
                    print('slow users is ', slow_users)
                    users_pre_pile = fast_users + slow_users
                    assert(len(users_pre_pile) == self.pile_num)
                    for i, user_pair in enumerate(users_pre_pile):
                        print(f'add user {user_pair} to pile {i}')
                        self.pile[i].charge_user.extend(user_pair)

                    for i in range(self.pile_num):
                        print(f'pile {i} charge user {self.pile[i].charge_user}')

                if tag == 0:
                    break

    def recovery(self, pile_id):
        mode = self.pile[pile_id].mode
        temp = []
        for i in range(self.pile_num):
            if i != pile_id and self.pile[i].status == 1 and self.pile[i].mode == mode:
                while len(self.pile[i].charge_user) >= 2:
                    temp.append(self.pile[i].charge_user.pop(1))
        temp.sort(key=lambda x:x.queue_number, reverse=False)
        print([i.user_id for i in self.priority_queue[mode]])
        self.priority_queue[mode].extend(temp)
        print([i.user_id for i in self.priority_queue[mode]])
        self.pile[pile_id].status = 1
        # print("-------recovery-------schedule-------")
        self.schedule()
         
    def find_best_pile(self, mode):
        # print("------------------")
        pos, min_len = -1, 100000000
        for i in range(self.pile_num):
            if self.pile[i].mode == mode and self.pile[i].status ==1 and len(self.pile[i].charge_user)<2:
                # print('find_best_pile:', 'mode: ', mode, 'pile_id: ', i, 'len: ', len(self.pile[i].charge_user), 'min_len: ', min_len, 'pos: ', pos)
                if len(self.pile[i].charge_user) == 0:
                    return i
                end_time = self.pile[i].get_wait_time()
                if min_len > end_time:
                    min_len = end_time
                    pos = i
                # print(i, utils.Time().get_time_str(end_time))
        return pos
        
    def find_priority_user(self, user_id, ispoped = False):
        for i in range(len(self.priority_queue)):
            for j in range(len(self.priority_queue[i])):
                if self.priority_queue[i][j].user_id == user_id:
                    if ispoped:
                        self.priority_queue[i].pop(j)
                    return True
        return False
    
    def find_waiting_user(self, user_id, ispoped = False):
        for i in range(len(self.waiting_queue)):
            for j in range(len(self.waiting_queue[i])):
                if self.waiting_queue[i][j].user_id == user_id:
                    if ispoped:
                        self.waiting_queue[i].pop(j)
                    return True
        return False
    
    def get_priority_queue_number(self, user_id):
        for i in range(len(self.priority_queue)):
            for j in range(len(self.priority_queue[i])):
                if self.priority_queue[i][j].user_id == user_id:
                    return self.priority_queue[i][j].queue_number, j
        return -1,-1
    
    def get_waiting_queue_number(self, user_id):
        for i in range(len(self.waiting_queue)):
            for j in range(len(self.waiting_queue[i])):
                if self.waiting_queue[i][j].user_id == user_id:
                    return self.waiting_queue[i][j].queue_number, j
        return -1, -1
    
    def get_charge_queue_number(self, user_id):
        for i in range(self.pile_num):
            for j in range(len(self.pile[i].charge_user)):
                if self.pile[i].charge_user[j].user_id == user_id:
                    return j, self.pile[i].charge_user[j].queue_number
        return -1, -1
    
    def find_charge_user(self, user_id, ispoped = False):
        for i in range(self.pile_num):
            for j in range(len(self.pile[i].charge_user)):
                if self.pile[i].charge_user[j].user_id == user_id:
                    if ispoped:
                        if j == 0:
                            self.bill_num+=1
                            print('-------end------', self.pile[i].charge_user[j].user_id)
                            _, _, new_bill = self.pile[i].end_charging(self.timer.get_time_sec(), 1, self.bill_num)
                            
                            if self.bill_dict.get(new_bill.user_id) == None:
                                self.bill_dict[new_bill.user_id] = [new_bill]
                            else:
                                self.bill_dict[new_bill.user_id].append(new_bill)
                        else:
                            self.pile[i].charge_user.pop(j)
                        self.schedule()
                    return True
        return False
          
    def query_pile_information(self):
        answer = []
        for i in range(self.pile_num):
            answer.append({"pile_id": i, "status": self.pile[i].status, "count": self.pile[i].total_count, "time": self.pile[i].total_time, "amount": self.pile[i].total_amount})
        return answer
    
    def query_waiting_queue(self,pile_id):
        answer = []
        for i in range(len(self.pile[pile_id].charge_user)):
            answer.append({"user_id": self.pile[pile_id].charge_user[i].user_id, "mode": self.pile[pile_id].charge_user[i].mode, "amount": self.pile[pile_id].charge_user[i].amount, "begin_wait": self.pile[pile_id].charge_user[i].begin_wait})
        # for i in range(2):
        #     for user in self.waiting_queue[i]:
        #         answer.append({"user_id": user.user_id, "mode": user.mode, "amount": user.amount, "begin_wait": user.begin_wait})
        # answer.sort(key = lambda x: x["begin_wait"])
        return answer        
        
    def get_h_m_s(self, t):
        # return {"h": t // 3600, "m": t % 3600 // 60, "s": t % 60}
        h = t // 3600
        m = t % 3600 // 60
        s = t % 60
        return f"{h}:{m}:{s}"
        
    def query_user_bill(self, user_id):
        bills = self.bill_dict.get(user_id)
        if bills == None:
            return None
        report = [{
            "bill_id": bill.bill_id,
            "time": self.get_h_m_s(bill.t),
            "duration": bill.cost_time,
            "pile_id": bill.pile_id,
            "volume": bill.amount,
            "charging_fee": bill.charge_fee,
            "service_fee": bill.service_fee,
            "overall": bill.total,
            "begin_time": self.get_h_m_s(bill.begin_time),
            "end_time": self.get_h_m_s(bill.end_time)
        } for bill in bills]
        return report

    def trans(self, x):
        return x
        # lis = ["F1", "F2", "T1", "T2", "T3"]
        # return lis[x]

    def query_pile_report(self):
        answer = []
        for i in range(self.pile_num):
            answer.append({"pile_id": self.trans(i), "charging_count": self.pile[i].total_times, "charging_duration": self.pile[i].total_time, "charging_volume": self.pile[i].total_amount, \
                "charging_fee": self.pile[i].charge_fee, "service_fee": self.pile[i].service_fee, "overall": self.pile[i].total_fee, "working":self.pile[i].status})
        return answer
        
    def error(self, pile_id):
        mode = self.pile[pile_id].mode
        if self.pile[pile_id].charge_user:
            self.bill_num+=1
            user, _, bill = self.pile[pile_id].end_charging(self.timer.get_time_sec(),2, self.bill_num)
            if self.bill_dict.get(bill.user_id) == None:
                self.bill_dict[bill.user_id] = [bill]
            else:
                self.bill_dict[bill.user_id].append(bill)
            self.priority_queue[mode].append(user)
            while self.pile[pile_id].charge_user:
                self.priority_queue[mode].append(self.pile[pile_id].charge_user.pop(0))
            print("error and len is ", len(self.pile[pile_id].charge_user))
        
        self.pile[pile_id].status = 0
        print([i.user_id for i in self.priority_queue[mode]])
        self.schedule()
        print([i.user_id for i in self.priority_queue[mode]])
        