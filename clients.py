from fastapi import APIRouter, Depends, HTTPException, Query,Request
from sqlalchemy.orm import Session
from database import get_db
import pandas as pd
from collections import Counter
import logging
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for data mappings
chat_mssg_counter = ""
taskid_formhand_map = {}
formhand_price_map = {}
client_ids_by_title = ""
user_ids_by_client_id = ""
chat_ids_by_user_id = ""
chat_taskid_map = {}
chat_prices = {}
title_handname_map = {}
formhand_title_map = {}
title_taskid_map = {}
user_id_email_map={}
user_id_chat_ids_map = {}
router = APIRouter()

def get_date_range(month_offset: int = 0):
    """
    Get the start and end date range for the given month offset.

    Parameters:
        month_offset (int): The number of months to offset from the current month.

    Returns:
        tuple: A tuple containing start and end dates.
    """
    # Calculate the first and last day of the month based on the offset
    current_date = datetime.now()
    first_day_of_month = (current_date.replace(day=1) - timedelta(days=30 * month_offset)).replace(day=1)
    last_day_of_month = (first_day_of_month.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

    return first_day_of_month, last_day_of_month


def get_chat_prices():
    """
    Fetch chat prices based on chat-to-task mapping.
    Returns a mapping of chat IDs to their corresponding execution prices.
    """
    chat_prices = {}
    for chat_id, task_id in chat_taskid_map.items():
        #logger.info("==>" + str(task_id))
        form_handler = taskid_formhand_map.get(task_id)
        if form_handler:
            execution_price = formhand_price_map.get(form_handler)
            if execution_price is not None:
                chat_prices[chat_id] = execution_price
            else:
                logger.warning(f"No price found for form handler: {form_handler}")
        else:
            logger.warning(f"No form handler found for task ID: {task_id}")

    #logger.info(f"Chat prices: {chat_prices}")
    return chat_prices




def calculate_detailed_costs(titlex):
    """
    Calculate costs split by handler names, task titles, and chat IDs.
    Returns a dictionary with detailed cost breakdown for each client.
    """
    chat_id_pricing = get_chat_prices()

    detailed_client_data = {}

    #for title in client_ids_by_title:
    chat_ids = get_chat_ids_by_client_name(titlex)
    handlers_cost = {}

    for chat_id in chat_ids:
        task_id = chat_taskid_map.get(chat_id)
        form_handler = taskid_formhand_map.get(task_id)
        if form_handler:
            handler_name = title_handname_map.get(form_handler, "Unknown Handler")
            task_title = title_taskid_map.get(task_id, "Unknown Task")

            if handler_name not in handlers_cost:
                handlers_cost[handler_name] = {}

            if task_title not in handlers_cost[handler_name]:
                handlers_cost[handler_name][task_title] = {'cost':[],'mssg_count':[]}

            handlers_cost[handler_name][task_title]['cost'].append(chat_id_pricing.get(chat_id, 0))
            handlers_cost[handler_name][task_title]['mssg_count'].append(chat_mssg_counter.get(chat_id, 0))

    try:
        for handler_namex in handlers_cost:
            for tasktitles in handlers_cost[handler_namex]:
                cost_isx = sum([cost * count for cost, count in zip(handlers_cost[handler_namex][tasktitles]['cost'], handlers_cost[handler_namex][tasktitles]['mssg_count'])])
                handlers_cost[handler_namex][tasktitles]['cost'] = str(cost_isx)
                handlers_cost[handler_namex][tasktitles]['mssg_count'] = sum(handlers_cost[handler_namex][tasktitles]['mssg_count'])
    except:
        pass
    detailed_client_data[titlex] = handlers_cost
    return detailed_client_data



def calculate_detailed_costs_email(titlex):
    """
    Calculate costs split by handler names, task titles, and chat IDs.
    Returns a dictionary with detailed cost breakdown for each client.
    """
    chat_id_pricing = get_chat_prices()
    detailed_client_data = {}
    chat_ids = get_chat_ids_by_client_name(titlex)
    handlers_cost = {}

    for chat_id in chat_ids:
        task_id = chat_taskid_map.get(chat_id)
        user_id = user_id_chat_ids_map.get(chat_id)
        email = user_id_email_map.get(user_id)
        form_handler = taskid_formhand_map.get(task_id)
        if email:
            handler_name = title_handname_map.get(form_handler, "Unknown Handler")
            task_title = title_taskid_map.get(task_id, "Unknown Task")

            if email not in handlers_cost:
                handlers_cost[email] = {}

            if task_title not in handlers_cost[email]:
                handlers_cost[email][task_title] = {'cost':[],'mssg_count':[]}

            handlers_cost[email][task_title]['cost'].append(chat_id_pricing.get(chat_id, 0))
            handlers_cost[email][task_title]['mssg_count'].append(chat_mssg_counter.get(chat_id, 0))

    try:
        for handler_namex in handlers_cost:
            for tasktitles in handlers_cost[handler_namex]:
                cost_isx = sum([cost * count for cost, count in zip(handlers_cost[handler_namex][tasktitles]['cost'], handlers_cost[handler_namex][tasktitles]['mssg_count'])])
                handlers_cost[handler_namex][tasktitles]['cost'] = str(cost_isx)
                handlers_cost[handler_namex][tasktitles]['mssg_count'] = sum(handlers_cost[handler_namex][tasktitles]['mssg_count'])
    except:
        pass

    detailed_client_data[titlex] = handlers_cost

    return detailed_client_data





def get_chat_ids_by_client_name(client_name):
    """
    Given a client name, this function returns all associated chat IDs.

    Parameters:
        client_name (str): The name of the client.

    Returns:
        list: A list of chat IDs associated with the given client name.
    """
    client_ids = client_ids_by_title.get(client_name, [])
    user_ids = []
    for client_id in client_ids:
        user_ids.extend(user_ids_by_client_id.get(client_id, []))

    chat_ids = []
    for user_id in user_ids:
        chat_ids.extend(chat_ids_by_user_id.get(user_id, []))

    return chat_ids


# Function to initialize data
def load_data(db: Session, start_date, end_date):
    global chat_mssg_counter, taskid_formhand_map, formhand_price_map, chat_taskid_map
    logger.info("Loading data...")

    try:
        # Load messages data filtered by created_time
        query = f"""
            SELECT chat_id FROM messages 
            WHERE created_time BETWEEN '{start_date}' AND '{end_date}';
        """
        logger.info("what date is query" + query)
        df = pd.read_sql_query(query, db.bind)
        chat_mssg_counter = Counter(df['chat_id'].to_list())

        # Fetch and group data from the 'chats' table filtered by created_time
        query = f"""
            SELECT id, task_id FROM chats 
            WHERE created_time BETWEEN '{start_date}' AND '{end_date}';
        """
        chats_df = pd.read_sql_query(query, db.bind)
        chat_task = chats_df.groupby('id')['task_id'].apply(list).to_dict()

        for client_idx, user_idx in chat_task.items():
            chat_taskid_map[client_idx] = user_idx[0]

        # Load tasks data without date filtering since it's not time-based
        query = "SELECT id, form_handler,title FROM tasks;"
        df = pd.read_sql_query(query, db.bind)
        taskid_formhand_ = df.groupby('id')['form_handler'].apply(list).to_dict()
        formhand_title_ = df.groupby('form_handler')['title'].apply(list).to_dict()
        title_taskid = df.groupby('id')['title'].apply(list).to_dict()

        for client_idx, user_idx in taskid_formhand_.items():
            taskid_formhand_map[client_idx] = user_idx[0]

        for client_idx, user_idx in formhand_title_.items():
            formhand_title_map[client_idx] = user_idx[0]

        for client_idx, user_idx in title_taskid.items():
            title_taskid_map[client_idx] = user_idx[0]


        # Load handler pricing data without date filtering
        query = "SELECT handler_name, execution_price FROM handler_pricing;"
        df = pd.read_sql_query(query, db.bind)
        formhand_price_ = df.groupby('handler_name')['execution_price'].apply(float).to_dict()

        for client_idx, user_idx in formhand_price_.items():
            formhand_price_map[client_idx] = user_idx

        # Load handler pricing data without date filtering
        query = "SELECT title,handler_name  FROM handler_pricing;"
        df = pd.read_sql_query(query, db.bind)
        title_handname = df.groupby('handler_name')['title'].apply(str).to_dict()

        for client_idx, user_idx in title_handname.items():
            title_handname_map[client_idx] = user_idx

        # Load handler pricing data without date filtering
        query = "SELECT id,email  FROM users;"
        df = pd.read_sql_query(query, db.bind)
        user_id_email = df.groupby('id')['email'].apply(list).to_dict()

        for client_idx, user_idx in user_id_email.items():
            user_id_email_map[client_idx] = user_idx[0]
    except Exception as e:
        logger.error(f"Error loading data: {e}")


# FastAPI startup event to load data
@router.on_event("startup")
async def startup_event():
    start_date, end_date = get_date_range()  # Load data for the current month by default
    with next(get_db()) as db:
        load_data(db, start_date, end_date)

#@router.get("/get-breakdown-data")
@router.post("/get-breakdown-data_email")
async def get_clients_data(request: Request):

    data = await request.json()
    client_id = data.get("client_id")
    task_name = data.get("task_name")
    breakdown = calculate_detailed_costs_email(client_id)
    return breakdown



#@router.get("/get-breakdown-data")
@router.post("/get-breakdown-data")
async def get_clients_data(request: Request):

    data = await request.json()
    client_id = data.get("client_id")
    task_name = data.get("task_name")
    # Calculate detailed costs
    breakdown = calculate_detailed_costs(client_id)
    #breakdown = calculate_detailed_costs_email(client_id)
    return breakdown




@router.get("/clients-data")
async def get_clients_data(
    db: Session = Depends(get_db),
    start_date: str = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(None, description="End date in YYYY-MM-DD format"),


    month_offset: int = Query(0, description="Offset in months from the current month (0 = current month, 1 = last month, etc.)")
):
    global client_ids_by_title, user_ids_by_client_id, chat_ids_by_user_id

    try:
        # Adjust the date range based on the offset
        if not start_date or not end_date:
            start_date, end_date = get_date_range(month_offset)
        load_data(db, start_date, end_date)

        # Fetch and group data from the 'clients' table filtered by created_time
        query = f"""
            SELECT id, title FROM clients;
        """
        logger.info(query)
        clients_df = pd.read_sql_query(query, db.bind)
        client_ids_by_title = clients_df.groupby('title')['id'].apply(list).to_dict()

        # Fetch and group data from the 'client_users' table filtered by modified_time
        query = f"""
            SELECT client_id, user_id FROM client_users;
        """
        client_users_df = pd.read_sql_query(query, db.bind)
        user_ids_by_client_id = client_users_df.groupby('client_id')['user_id'].apply(list).to_dict()

        # Fetch and group data from the 'chats' table filtered by created_time
        query = f"""
            SELECT id, user_id FROM chats 
            WHERE created_time BETWEEN '{start_date}' AND '{end_date}';
        """
        chats_df = pd.read_sql_query(query, db.bind)
        chat_ids_by_user_id = chats_df.groupby('user_id')['id'].apply(list).to_dict()
        user_id_chat_ids_ = chats_df.groupby('id')['user_id'].apply(list).to_dict()
        for client_idx, user_idx in user_id_chat_ids_.items():
            user_id_chat_ids_map[client_idx] = user_idx[0]
        chat_id_pricing = get_chat_prices()
        # Calculate chat costs for each client
        client_chat_data = []
        for title in client_ids_by_title:
            
            chat_ids = get_chat_ids_by_client_name(title)
            cost_is_ = [chat_id_pricing.get(chater_id, 0) for chater_id in chat_ids]
            msg_count = [chat_mssg_counter.get(chater_id, 0) for chater_id in chat_ids]
            cost_is = sum([cost * count for cost, count in zip(cost_is_, msg_count)])

            client_chat_data.append({'client': title, 'cost': str(cost_is)})

        return client_chat_data

    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching data: {e}")
