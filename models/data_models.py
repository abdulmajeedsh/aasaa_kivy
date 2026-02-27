from dataclasses import dataclass


@dataclass
class LoginInfo:
    username: str = ""
    password: str = ""
    user_type: str = "Bookman"
    phone_id: str = ""


@dataclass
class Branch:
    branch_code: str = ""
    branch_name: str = ""
    user_code: str = ""


@dataclass
class Route:
    route_code: str = ""
    route_name: str = ""
    branch_code: str = ""
    complete_bit: int = 0
    mandatory_bit: int = 0


@dataclass
class Region:
    region_code: str = ""
    region_name: str = ""
    route_code: str = ""
    parent_region_code: str = ""
    complete_bit: int = 0
    mandatory_bit: int = 0


@dataclass
class Customer:
    customer_code: str = ""
    customer_name: str = ""
    contact: str = ""
    address: str = ""
    region_code: str = ""
    sub_region_code: str = ""
    route_code: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    complete_bit: int = 0
    sync_bit: int = 0
    placed_order_check: int = 0
    order_counter: int = 0
    mandatory_bit: int = 0


@dataclass
class Product:
    product_code: str = ""
    product_name: str = ""
    unit_price: float = 0.0
    company: str = ""
    is_focused: int = 0


@dataclass
class OrderDetail:
    id: int = 0
    customer_code: str = ""
    product_code: str = ""
    product_name: str = ""
    unit_price: float = 0.0
    discount_amount: float = 0.0
    discount_type: str = ""
    quantity: int = 0
    net_amount: float = 0.0
    total_amount: float = 0.0
    branch_code: str = ""
    order_id: str = ""
    sync_bit: int = 0
    close_bit: int = 0
    no_order: int = 0
    reason: str = ""
    immediate: int = 0
    x_co: float = 0.0
    y_co: float = 0.0
    x_co_close: float = 0.0
    y_co_close: float = 0.0
    edit_mode: int = 0
    android_order_id: str = ""
    timestamp_start: str = ""
    timestamp_end: str = ""
    timestamp_start_customer: str = ""


@dataclass
class TempOrder:
    customer_code: str = ""
    product_code: str = ""
    product_name: str = ""
    unit_price: float = 0.0
    quantity: int = 0
    net_amount: float = 0.0
    total_amount: float = 0.0
    order_id: str = ""
    disc_type: str = ""
    discount: float = 0.0


@dataclass
class ErrorLog:
    id: int = 0
    branch_code: str = ""
    error_details: str = ""
    timestamp: str = ""


@dataclass
class BookingRecord:
    customer_code: str = ""
    customer_name: str = ""
    total_amount: float = 0.0
    date: str = ""
    branch_code: str = ""


@dataclass
class CompanySales:
    company: str = ""
    target_amount: float = 0.0
    actual_amount: float = 0.0
    month: str = ""


@dataclass
class UnsyncedCustomer:
    customer_code: str = ""
    customer_name: str = ""
    order_count: int = 0
    total_amount: float = 0.0
