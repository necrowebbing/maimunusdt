from aiogram.fsm.state import StatesGroup, State

class ReferrerID(StatesGroup):
    id = State()

class CallbackStates(StatesGroup):
    promocode = State()
    withdraw_sum_cb = State()

class AdminStates(StatesGroup):
    new_promocode_form = State()
    piar_data = State()
    promocode_id_for_del = State()
    user_find_data = State()
    attached_user_id = State()
    user_change_money_m_data = State()
    user_change_money_p_data = State()
    json_data = State()
    price_data_db = State()
    price_data_rb = State()
    price_data_mw = State()
    price_data_rw = State()
    newop = State()
    delop = State()
    bankAddSum = State()

class ReferralSponsors(StatesGroup):
    piarflow_sponsors_list = State() 
