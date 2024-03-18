import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('restaurant_reviews.db')
cursor = conn.cursor()

class Restaurant:
    def __init__(self, id, name, price):
        self.id = id
        self.name = name
        self.price = price

    def reviews(self):
        # Returns a collection of all the reviews for the Restaurant
        cursor.execute('SELECT * FROM reviews WHERE restaurant_id = ?', (self.id,))
        return cursor.fetchall()

    def customers(self):
        # Returns a collection of all the customers who reviewed the Restaurant
        cursor.execute('''
        SELECT customers.* FROM customers
        JOIN reviews ON customers.id = reviews.customer_id
        WHERE reviews.restaurant_id = ?
        ''', (self.id,))
        return cursor.fetchall()


class Customer:
    def __init__(self, id, first_name, last_name):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name

    def reviews(self):
        # Returns a collection of all the reviews that the Customer has left
        cursor.execute('SELECT * FROM reviews WHERE customer_id = ?', (self.id,))
        return cursor.fetchall()

    def restaurants(self):
        # Returns a collection of all the restaurants that the Customer has reviewed
        cursor.execute('''
        SELECT restaurants.* FROM restaurants
        JOIN reviews ON restaurants.id = reviews.restaurant_id
        WHERE reviews.customer_id = ?
        ''', (self.id,))
        return cursor.fetchall()

    def full_name(self):
        # Returns the full name of the customer, with the first name and the last name concatenated, Western style.
        return f"{self.first_name} {self.last_name}"

    def favorite_restaurant(self):
        # Returns the restaurant instance that has the highest star rating from this customer
        cursor.execute('''
        SELECT restaurants.*, MAX(reviews.star_rating) AS max_rating FROM restaurants
        JOIN reviews ON restaurants.id = reviews.restaurant_id
        WHERE reviews.customer_id = ?
        ''', (self.id,))
        restaurant_data = cursor.fetchone()
        return Restaurant(*restaurant_data) if restaurant_data else None

    def add_review(self, restaurant, rating):
        # Creates a new review for the restaurant with the given restaurant_id
        cursor.execute('INSERT INTO reviews (customer_id, restaurant_id, star_rating) VALUES (?, ?, ?)',
                       (self.id, restaurant.id, rating))
        conn.commit()

    def delete_reviews(self, restaurant):
        # Removes all their reviews for this restaurant
        cursor.execute('DELETE FROM reviews WHERE customer_id = ? AND restaurant_id = ?',
                       (self.id, restaurant.id))
        conn.commit()


class Review:
    def __init__(self, id, customer_id, restaurant_id, star_rating):
        self.id = id
        self.customer_id = customer_id
        self.restaurant_id = restaurant_id
        self.star_rating = star_rating

    def customer(self):
        # Returns the Customer instance for this review
        cursor.execute('SELECT * FROM customers WHERE id = ?', (self.customer_id,))
        customer_data = cursor.fetchone()
        return Customer(*customer_data) if customer_data else None

    def restaurant(self):
        # Returns the Restaurant instance for this review
        cursor.execute('SELECT * FROM restaurants WHERE id = ?', (self.restaurant_id,))
        restaurant_data = cursor.fetchone()
        return Restaurant(*restaurant_data) if restaurant_data else None

    def full_review(self):
        # Returns a string formatted as Review for {insert restaurant name} by {insert customer's full name}: {insert review star_rating} stars.
        customer = self.customer()
        restaurant = self.restaurant()
        if customer and restaurant:
            return f"Review for {restaurant.name} by {customer.full_name()}: {self.star_rating} stars."
        else:
            return "Review not found."


# Sample data creation
def create_sample_data(cursor):
    # Creating sample restaurants
    cursor.execute('INSERT INTO restaurants (name, price) VALUES (?, ?)', ('Restaurant A', 3))
    cursor.execute('INSERT INTO restaurants (name, price) VALUES (?, ?)', ('Restaurant B', 2))

    # Creating sample customers
    cursor.execute('INSERT INTO customers (first_name, last_name) VALUES (?, ?)', ('John', 'Doe'))
    cursor.execute('INSERT INTO customers (first_name, last_name) VALUES (?, ?)', ('Jane', 'Smith'))

    # Creating sample reviews
    cursor.execute('INSERT INTO reviews (customer_id, restaurant_id, star_rating) VALUES (?, ?, ?)', (1, 1, 4))
    cursor.execute('INSERT INTO reviews (customer_id, restaurant_id, star_rating) VALUES (?, ?, ?)', (2, 2, 5))

    conn.commit()


# Testing the code
create_sample_data(cursor)

# Fetching and testing relationships
restaurant = Restaurant(1, 'Restaurant A', 3)
customer = Customer(1, 'John', 'Doe')
review = Review(1, 1, 1, 4)

print(restaurant.reviews())  # Should print the review for Restaurant A
print(customer.restaurants())  # Should print the restaurant reviewed by John Doe
print(review.full_review())  # Should print the full review text
