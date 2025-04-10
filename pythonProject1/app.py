from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1@localhost:5432/kursochBUB3'

db = SQLAlchemy(app)

# Модели
class Order(db.Model):  # заказ
    id_order = db.Column(db.Integer, primary_key=True)  # айди заказа
    Seller_id = db.Column(db.Integer, nullable=False)  # айди продавца
    Menager_id = db.Column(db.Integer, nullable=False)  # айди менеджера склада
    fio_buyer = db.Column(db.String(50), nullable=False)  # фио покупателя
    buyer_phone = db.Column(db.Integer, nullable=False)  # телефон покупателя
    id_equipment = db.Column(db.Integer, nullable=False)  # айди запчасти
    id_spare = db.Column(db.Integer, nullable=False)  # айди техники
    availability = db.Column(db.String(50), nullable=False)  # статус заказа


class Manager(db.Model):  # менеджер склада
    Menager_id = db.Column(db.Integer, primary_key=True)  # менеджер айди
    fio_Manager = db.Column(db.String(50), nullable=False)  # фио менеджера


class Equipment(db.Model):  # запчасти
    id_equipment = db.Column(db.Integer, primary_key=True)  # айди
    numder_of_units = db.Column(db.Integer, nullable=False)  # кол-во единиц
    availability = db.Column(db.String(50), nullable=False)  # состояние
    price_per_unit = db.Column(db.Integer, nullable=False)  # цена
    name = db.Column(db.String(100), nullable=False)  # название


class Spare_parts(db.Model):  # техника
    id_spare = db.Column(db.Integer, primary_key=True)  # айди техники
    numder_units = db.Column(db.Integer, nullable=False)  # кол-во единиц
    availability = db.Column(db.String(50), nullable=False)  # состояние
    price_per_unit = db.Column(db.Integer, nullable=False)  # цена
    name = db.Column(db.String(100), nullable=False)  # название


class warehouse_cell(db.Model):  # склад
    cell_id = db.Column(db.Integer, primary_key=True)  # айди ячейки склада
    status = db.Column(db.String(50), nullable=False)  # статус ячейки
    id_equipment = db.Column(db.Integer, nullable=False)  # айди запчасти в ячейке


class parking_space(db.Model):  # парковка
    parking_id = db.Column(db.Integer, primary_key=True)  # айди парковочного места
    id_spare = db.Column(db.Integer, nullable=False)  # айди техники припаркованной на месте
    status = db.Column(db.String(50), nullable=False)  # статус места


class order_tex(db.Model):  # доп. таблица по технике в заказе
    id_order_tex = db.Column(db.Integer, primary_key=True)  # айди
    id_order = db.Column(db.Integer, nullable=False)  # айди заказа
    id_spare = db.Column(db.Integer, nullable=False)  # айди техники
    col_vo = db.Column(db.Integer, nullable=False)  # кол-во единиц


class order_eq(db.Model):  # доп. таблица по запчастям в заказе
    id_order_eq = db.Column(db.Integer, primary_key=True)  # айди
    id_order = db.Column(db.Integer, nullable=False)  # айди заказа
    id_equipment = db.Column(db.Integer, nullable=False)  # айди запчасти
    col_vo = db.Column(db.Integer, nullable=False)  # кол-во единиц в заказе


@app.route('/')
def index():
    return redirect('/all_database')


@app.route('/all_database')
def all_database():
    orders = Order.query.all()
    manager = Manager.query.all()
    equipments = Equipment.query.all()
    spare_parts = Spare_parts.query.all()
    warehouse = warehouse_cell.query.all()
    parking = parking_space.query.all()
    col_tex = order_tex.query.all()
    col_eq = order_eq.query.all()

    return render_template('all_database.html', orders=orders,
                           manager=manager,
                           equipments=equipments,
                           spare_parts=spare_parts,
                           warehouse=warehouse,
                           parking=parking,
                           col_tex=col_tex,
                           col_eq=col_eq)

@app.route('/order', methods=['GET', 'POST'])
def create_order():
    if request.method == 'POST':
        # Извлечение данных из формы
        seller_id = request.form.get('Seller_id')
        manager_id = request.form.get('Menager_id')
        fio_buyer = request.form.get('fio_buyer')
        buyer_phone = request.form.get('buyer_phone')
        availability = request.form.get('availability')

        # Проверка обязательных полей
        if not seller_id:
            return 'Выберите номер продавца'
        if not manager_id:
            return 'Выберите номер менеджера'
        if not availability:
            return 'Выберите статус'

        try:
            # Создание основного заказа
            main_order = Order(
                Seller_id=seller_id,
                Menager_id=manager_id,
                fio_buyer=fio_buyer,
                buyer_phone=buyer_phone,
                availability=availability
            )
            db.session.add(main_order)
            db.session.commit()

            main_order_id = main_order.id_order

            # Добавление запчастей
            equipment_ids = request.form.getlist('id_equipment')  # Список ID запчастей
            equipment_counts = request.form.getlist('col_eq')  # Количество каждой запчасти
            for eq_id, count in zip(equipment_ids, equipment_counts):
                if eq_id and int(count) > 0:  # Проверяем, что данные корректны
                    # Создаем новую строку заказа для каждой запчасти
                    order_data = {
                        'Seller_id': seller_id,
                        'Menager_id': manager_id,
                        'fio_buyer': fio_buyer,
                        'buyer_phone': buyer_phone,
                        'id_equipment': eq_id,
                        'availability': availability
                    }
                    new_order = Order(**order_data)
                    db.session.add(new_order)
                    db.session.commit()

                    # Добавляем запись в таблицу order_eq
                    col_eq_data = {
                        'id_order': new_order.id_order,
                        'id_equipment': eq_id,
                        'col_vo': count
                    }
                    coli_eq = order_eq(**col_eq_data)
                    db.session.add(coli_eq)

            # Добавление техники
            spare_ids = request.form.getlist('id_spare')  # Список ID техники
            spare_counts = request.form.getlist('col_tex')  # Количество каждой единицы техники
            for sp_id, count in zip(spare_ids, spare_counts):
                if sp_id and int(count) > 0:  # Проверяем, что данные корректны
                    # Создаем новую строку заказа для каждой единицы техники
                    order_data = {
                        'Seller_id': seller_id,
                        'Menager_id': manager_id,
                        'fio_buyer': fio_buyer,
                        'buyer_phone': buyer_phone,
                        'id_spare': sp_id,
                        'availability': availability
                    }
                    new_order = Order(**order_data)
                    db.session.add(new_order)
                    db.session.commit()

                    # Добавляем запись в таблицу order_tex
                    col_tex_data = {
                        'id_order': new_order.id_order,
                        'id_spare': sp_id,
                        'col_vo': count
                    }
                    coli_tex = order_tex(**col_tex_data)
                    db.session.add(coli_tex)

            db.session.commit()
            return redirect('/all_database')

        except ValueError:  # Обработка ошибки преобразования строки в число
            db.session.rollback()  # Откатываем изменения
            return 'Некорректное значение количества запчастей или техники'

        except Exception as e:
            db.session.rollback()  # Откатываем изменения
            return f'При добавлении заказа произошла ошибка: {e}'

    # Если метод GET, показываем форму создания заказа
    managers = Manager.query.all()
    equipments = Equipment.query.all()
    spares = Spare_parts.query.all()
    return render_template('ty.html', managers=managers, equipments=equipments, spares=spares)

@app.route('/order/<int:id_order>/delete', methods=['GET', 'POST'])
def delete_order(id_order):
    order = Order.query.get(id_order)
    if not order:
        return "Заказ не найден", 404

    # Проверяем, что заказ не выдан
    if order.availability != "Не выдан":
        return "Можно удалить только не выданные заказы"

    if request.method == 'POST':
        try:
            # Удаляем связанные записи из таблиц order_eq и order_tex
            order_eq.query.filter_by(id_order=id_order).delete()
            order_tex.query.filter_by(id_order=id_order).delete()

            # Удаляем сам заказ
            db.session.delete(order)
            db.session.commit()
            return redirect('/all_database')
        except Exception as e:
            return f'Ошибка при удалении заказа: {e}'

    # Если метод GET, показываем страницу подтверждения удаления
    return render_template('confirm_delete_order.html', order=order)

@app.route('/order/<int:id_order>/change_status', methods=['POST'])
def change_order_status(id_order):
    order = Order.query.get(id_order)
    if not order:
        return "Заказ не найден", 404

    new_status = request.form.get('availability')
    if not new_status:
        return 'Выберите новый статус'

    try:
        # Если статус меняется на "Выдан"
        if new_status == "Выдан" and order.availability == "Не выдан":
            # Уменьшаем количество запчастей
            order_equipments = order_eq.query.filter_by(id_order=id_order).all()
            for eq in order_equipments:
                equipment = Equipment.query.get(eq.id_equipment)
                if equipment:
                    equipment.numder_of_units -= eq.col_vo
                    db.session.commit()

            # Уменьшаем количество техники
            order_spares = order_tex.query.filter_by(id_order=id_order).all()
            for sp in order_spares:
                spare = Spare_parts.query.get(sp.id_spare)
                if spare:
                    spare.numder_units -= sp.col_vo
                    db.session.commit()

        # Обновляем статус заказа
        order.availability = new_status
        db.session.commit()
        return redirect('/all_database')

    except Exception as e:
        return f'Ошибка при изменении статуса заказа: {e}'

@app.route('/order/<int:id_order>/change_status_form', methods=['GET'])
def change_order_status_form(id_order):
    order = Order.query.get(id_order)
    if not order:
        return "Заказ не найден", 404
    return render_template('change_order_status.html', order=order)

@app.route('/menager', methods=['GET', 'POST'])
def menager():
   if request.method == 'POST':
        fio_manager = request.form['fio_Manager']

        menager=Manager(fio_Manager=fio_manager)
        try:
          db.session.add(menager)
          db.session.commit()
          return redirect('/')
        except:
          return 'При добавлении произошла ошибка'
   else:
        return render_template('Menager.html')
@app.route('/menager/<int:Menager_id>/delete', methods=['GET', 'POST'])
def delete_menager(Menager_id):
    menager = Manager.query.get(Menager_id)
    if request.method == 'POST':
        try:
            db.session.delete(menager)
            db.session.commit()
            return redirect('/')  # Здесь измените на нужный маршрут
        except Exception as e:
            return f'При удалении заказа произошла ошибка! {e}'
    # Если метод GET, возвращаем страницу подтверждения удаления
    return render_template('confirm_delete.html', item=menager)
@app.route('/menager/<int:Menager_id>/upd', methods=['GET', 'POST'])
def update_menager(Menager_id):
    menager = Manager.query.get(Menager_id)
    if request.method == 'POST':
        try:
            # Получаем данные из формы
            menager.fio_Manager = request.form.get('fio_Manager')


            db.session.commit()
            return redirect('/menager')  # Здесь измените на нужный маршрут
        except Exception as e:
            return f'При обновлении заказа произошла ошибка! {e}'
    else:
        return render_template('upd_manager.html', menager=menager)

@app.route('/equipment', methods=['GET', 'POST'])
def equipment():
    if request.method == 'POST':
        # Получение данных из формы
        numder_of_units = int(request.form['numder_of_units'])
        availability = request.form['availability']
        price_per_unit = int(request.form['price_per_unit'])
        name = request.form['name']

        # Создание нового оборудования
        equipment = Equipment(

            numder_of_units=numder_of_units,
            availability=availability,
            price_per_unit=price_per_unit,
            name=name
        )

        try:
            db.session.add(equipment)
            db.session.commit()

            # Если статус "В наличии" и есть единицы товара
            if availability == "В наличии" and numder_of_units > 0:
                free_cells = warehouse_cell.query.filter_by(status="свободно").all()
                if len(free_cells) >= numder_of_units:
                    for _ in range(numder_of_units):
                        cell = free_cells.pop(0)
                        cell.status = "занято"
                        cell.id_equipment = equipment.id_equipment
                        db.session.commit()
                else:
                    return f"Недостаточно свободных ячеек склада! Требуется {numder_of_units}, доступно {len(free_cells)}."

            return redirect('/')
        except Exception as e:
            return f'При добавлении произошла ошибка: {e}'
    else:

        availability_options = ["В наличии", "Заказано", "Нет в наличии"]  # Статусы
        return render_template('equipment.html',  availability_options=availability_options)
@app.route('/equipment/<int:id_equipment>/upd', methods=['GET', 'POST'])
def update_equipment(id_equipment):
    equipment = Equipment.query.get(id_equipment)
    if not equipment:
        return "Запчасть не найдена", 404

    if request.method == 'POST':
        try:
            # Обновление данных оборудования
            new_num_units = int(request.form.get('numder_of_units'))
            equipment.availability = request.form.get('availability')
            equipment.price_per_unit = int(request.form.get('prce_per_unit'))
            equipment.name = request.form.get('name')

            # Если статус "В наличии" и количество изменилось
            if equipment.availability == "В наличии":
                current_units = equipment.numder_of_units
                diff = new_num_units - current_units

                if diff > 0:  # Нужно занять новые ячейки
                    free_cells = warehouse_cell.query.filter_by(status="свободно").limit(diff).all()
                    if len(free_cells) < diff:
                        return f"Недостаточно свободных ячеек склада! Требуется {diff}, доступно {len(free_cells)}."
                    for cell in free_cells:
                        cell.status = "занято"
                        cell.id_equipment = id_equipment
                        db.session.commit()

                elif diff < 0:  # Нужно освободить ячейки
                    occupied_cells = warehouse_cell.query.filter_by(id_equipment=id_equipment).limit(abs(diff)).all()
                    for cell in occupied_cells:
                        cell.status = "свободно"
                        cell.id_equipment = None
                        db.session.commit()

            equipment.numder_of_units = new_num_units
            db.session.commit()
            return redirect('/equipment')
        except Exception as e:
            return f'При обновлении произошла ошибка! {e}'
    else:
        # Получаем всех менеджеров и доступные статусы
        availability_options = ["В наличии", "Заказано", "Нет в наличии"]  # Статусы
        return render_template('upd_equipment.html', equipment=equipment, availability_options=availability_options)
@app.route('/equipment/<int:id_equipment>/delete', methods=['GET', 'POST'])
def delete_equipment(id_equipment):
    equipment = Equipment.query.get(id_equipment)
    if request.method == 'POST':
        try:
            # Освобождаем ячейки склада
            occupied_cells = warehouse_cell.query.filter_by(id_equipment=id_equipment).all()
            for cell in occupied_cells:
                cell.status = "свободно"
                cell.id_equipment = None
                db.session.commit()

            db.session.delete(equipment)
            db.session.commit()
            return redirect('/')  # Здесь измените на нужный маршрут
        except Exception as e:
            return f'При удалении произошла ошибка! {e}'
    # Если метод GET, возвращаем страницу подтверждения удаления
    return render_template('confirm_delete.html', item=equipment)


@app.route('/spare_parts', methods=['GET', 'POST'])
def spare_parts():
    if request.method == 'POST':

        numb_units = int(request.form['numb_units'])
        availability = request.form['availability']
        price_per_unit = int(request.form['price_per_unit'])
        name = request.form['name']

        spare_parts = Spare_parts(

            numder_units=numb_units,
            availability=availability,
            price_per_unit=price_per_unit,
            name=name
        )

        try:
            db.session.add(spare_parts)
            db.session.commit()

            # Если статус "В наличии" и есть единицы товара
            if availability == "В наличии" and numb_units > 0:
                free_parking = parking_space.query.filter_by(status="свободно").all()
                if len(free_parking) >= numb_units:
                    for _ in range(numb_units):
                        park = free_parking.pop(0)
                        park.status = "занято"
                        park.id_spare = spare_parts.id_spare
                        db.session.commit()
                else:
                    return f"Недостаточно свободных мест на парковке! Требуется {numb_units}, доступно {len(free_parking)}."

            return redirect('/')
        except Exception as e:
            return f'При добавлении произошла ошибка: {e}'
    else:

        availability_options = ["В наличии", "Заказано", "Нет в наличии"]
        return render_template('spare_parts.html',  availability_options=availability_options)

@app.route('/spare_parts/<int:id_spare>/delete', methods=['GET', 'POST'])
def delete_spare_parts(id_spare):
    spare_parts = Spare_parts.query.get(id_spare)
    if request.method == 'POST':
        try:
            # Освобождаем места на парковке
            occupied_parking = parking_space.query.filter_by(id_spare=id_spare).all()
            for park in occupied_parking:
                park.status = "свободно"
                park.id_spare = None
                db.session.commit()

            db.session.delete(spare_parts)
            db.session.commit()
            return redirect('/')  # Здесь измените на нужный маршрут
        except Exception as e:
            return f'При удалении произошла ошибка! {e}'
    # Если метод GET, возвращаем страницу подтверждения удаления
    return render_template('confirm_delete.html', item=spare_parts)
@app.route('/spare_parts/<int:id_spare>/upd', methods=['GET', 'POST'])
def update_spare_parts(id_spare):
    spare_parts = Spare_parts.query.get(id_spare)
    if not spare_parts:
        return "Техника не найдена", 404

    if request.method == 'POST':
        try:

            new_num_units = int(request.form.get('numder_units'))
            spare_parts.availability = request.form.get('availability')
            spare_parts.price_per_unit = int(request.form.get('price_per_unit'))
            spare_parts.name = request.form.get('name')

            # Если статус "В наличии" и количество изменилось
            if spare_parts.availability == "В наличии":
                current_units = spare_parts.numder_units
                diff = new_num_units - current_units

                if diff > 0:  # Нужно занять новые места
                    free_parking = parking_space.query.filter_by(status="свободно").limit(diff).all()
                    if len(free_parking) < diff:
                        return f"Недостаточно свободных мест на парковке! Требуется {diff}, доступно {len(free_parking)}."
                    for park in free_parking:
                        park.status = "занято"
                        park.id_spare = id_spare
                        db.session.commit()

                elif diff < 0:  # Нужно освободить места
                    occupied_parking = parking_space.query.filter_by(id_spare=id_spare).limit(abs(diff)).all()
                    for park in occupied_parking:
                        park.status = "свободно"
                        park.id_spare = None
                        db.session.commit()

            spare_parts.numder_units = new_num_units
            db.session.commit()
            return redirect('/all_database')
        except Exception as e:
            return f'При обновлении произошла ошибка! {e}'
    else:

        availability_options = ["В наличии", "Заказано", "Нет в наличии"]
        return render_template('upd_spare_parts.html', spare_parts=spare_parts,  availability_options=availability_options)



@app.route('/parking_report', methods=['GET'])
def parking_report():
    parking=parking_space.query.all()
    report_data=[]
    for parkings in parking:
        parking=parking_space.query.get(parkings.parking_id)
        spare_parts = Spare_parts.query.get(parkings.id_spare)
        spare_parts_name = spare_parts.name if spare_parts else "Неизвестно"
        spare_parts_price = spare_parts.price_per_unit if spare_parts else 0
        spare_parts_quantity = spare_parts.numder_units if spare_parts else 0

        report_data.append({
            'Номер места':parkings.parking_id,
            'статус':parking.status,
            'наз_тех':spare_parts_name,
            'цена':spare_parts_price,
            'количество':spare_parts_quantity,

        })


    return render_template('parking_report.html', report_data=report_data)


@app.route('/order_report', methods=['GET'])
def order_report():
    orders = Order.query.all()  # Получаем все заказы
    report_data = []  # Список для хранения данных отчета

    for order in orders:
        # Получаем менеджера для заказа
        manager = Manager.query.filter_by(Menager_id=order.Menager_id).first()
        if manager:
            fio_Manager = manager.fio_Manager  # Если менеджер найден, берем ФИО
        else:
            fio_Manager = 'Не найдено'

          # Получаем запчасти для заказа
        spare_parts = Spare_parts.query.filter_by(id_spare=order.id_spare).first()
        if spare_parts:
                naz_spare_parts = spare_parts.name  # Если запчасти найдены, берем название
        else:
                naz_spare_parts = 'Не найдено'

        # Получаем оборудование для заказа
        equipment = Equipment.query.filter_by(id_equipment=order.id_equipment).first()
        if equipment:
            naz_equipment = equipment.name  # Если оборудование найдено, берем название
        else:
            naz_equipment = 'Не найдено'



        # Используем поле availability для отображения статуса
        order_status = order.availability

        # Добавляем данные о заказе в список отчета
        report_data.append({
            'ном.заказа': order.id_order,
            'фио_мен': fio_Manager,
            'фио_покуп': order.fio_buyer,
            'наз_тех': naz_spare_parts,
            'наз_запчасти': naz_equipment,
            'availability': order_status,
        })

    # Отправляем данные в шаблон
    return render_template('order_report.html', report_data=report_data)





if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)