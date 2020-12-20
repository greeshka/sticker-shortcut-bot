def first_interaction_setup(update, mycursor):
    '''Sets up tables for a new user'''

    add_to_user_info(update, mycursor)
    add_private_pack_to_pack_info(update, mycursor)
    add_packs_to_user_packs(update, mycursor)


def add_to_user_info(update, mycursor):
    '''adds new user to user_info'''
    user_data = {}
    user_data['user_id'] = update.message.from_user.id
    user_data['username'] = update.message.chat.username
    user_data['language_code'] = update.message.from_user.language_code
    user_data['call_dttm'] = update.message.date.strftime(
        '%Y-%m-%d %H:%M:%S')

    sql = '''insert into user_info
        values (%s, %s, %s, %s);'''
    val = (
        user_data['user_id'], user_data['username'],
        user_data['language_code'], user_data['call_dttm']
    )
    mycursor.execute(sql, val)


def add_private_pack_to_pack_info(update, mycursor):
    '''creates private pack for a new user'''
    user_data = {}
    user_data['pack_name'] = 'private'
    user_data['pack_author_id'] = update.message.from_user.id
    user_data['create_dttm'] = update.message.date.strftime(
        '%Y-%m-%d %H:%M:%S')

    sql = '''insert into pack_info (
        pack_name, pack_author_id, create_dttm)
        values (%s, %s, %s)'''
    val = (
        user_data['pack_name'], user_data['pack_author_id'],
        user_data['create_dttm']
    )
    mycursor.execute(sql, val)


def add_packs_to_user_packs(update, mycursor):
    '''adds default pack and user\'s private pack to user_packs'''
    user_data = {}
    user_data['user_id'] = update.message.from_user.id
    user_data['added_dttm'] = update.message.date.strftime(
        '%Y-%m-%d %H:%M:%S')

    sql = '''
        select pack_id from pack_info
        where
            pack_author_id = %s
            and pack_name = "private"
            '''
    val = (update.message.from_user.id,)
    mycursor.execute(sql, val)

    result = mycursor.fetchall()
    private_pack_id = result[0][0]

    sql = '''insert into user_packs
        values (%s, %s, %s)'''
    val = [
        [user_data['user_id'], 1, user_data['added_dttm']],
        [user_data['user_id'], private_pack_id, user_data['added_dttm']]
        ]
    mycursor.executemany(sql, val)
