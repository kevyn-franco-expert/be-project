from pydantic import BaseModel, EmailStr, validator
from datetime import date, datetime
from typing import Optional
from enum import Enum

class VehicleStatus(str, Enum):
    available = "available"
    rented = "rented"
    maintenance = "maintenance"

class BookingStatus(str, Enum):
    confirmed = "confirmed"
    completed = "completed"
    cancelled = "cancelled"

class PaymentStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    refunded = "refunded"

class VehicleTypeEnum(str, Enum):
    small_car = "small_car"
    suv = "suv"
    van = "van"

# User Schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: str
    
    @validator('name')
    def validate_name(cls, v):
        if len(v) < 2:
            raise ValueError('Name must be at least 2 characters long')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        if len(v) < 10:
            raise ValueError('Phone must be at least 10 characters long')
        return v

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Vehicle Type Schemas
class VehicleTypeBase(BaseModel):
    name: VehicleTypeEnum
    capacity: int
    daily_rate: float
    
    @validator('capacity')
    def validate_capacity(cls, v):
        if v <= 0:
            raise ValueError('Capacity must be greater than 0')
        return v
    
    @validator('daily_rate')
    def validate_daily_rate(cls, v):
        if v <= 0:
            raise ValueError('Daily rate must be greater than 0')
        return v

class VehicleTypeResponse(VehicleTypeBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Vehicle Schemas
class VehicleBase(BaseModel):
    type_id: int
    model: str
    year: int
    license_plate: str
    color: Optional[str] = None
    status: VehicleStatus = VehicleStatus.available
    
    @validator('year')
    def validate_year(cls, v):
        current_year = datetime.now().year
        if v < 1990 or v > current_year + 1:
            raise ValueError(f'Year must be between 1990 and {current_year + 1}')
        return v
    
    @validator('license_plate')
    def validate_license_plate(cls, v):
        if len(v) < 3:
            raise ValueError('License plate must be at least 3 characters long')
        return v

class VehicleCreate(VehicleBase):
    pass

class VehicleUpdate(VehicleBase):
    pass

class VehicleResponse(VehicleBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    vehicle_type: VehicleTypeResponse
    
    class Config:
        from_attributes = True

class VehicleAvailabilityResponse(VehicleResponse):
    type_name: str
    capacity: int

# Booking Schemas
class BookingBase(BaseModel):
    user_id: int
    vehicle_id: int
    pickup_date: date
    return_date: date
    
    @validator('return_date')
    def validate_dates(cls, v, values):
        if 'pickup_date' in values and v <= values['pickup_date']:
            raise ValueError('Return date must be after pickup date')
        
        if 'pickup_date' in values:
            rental_days = (v - values['pickup_date']).days
            if rental_days > 7:
                raise ValueError('Rental period cannot exceed 7 days')
            
            advance_days = (values['pickup_date'] - date.today()).days
            if advance_days > 7:
                raise ValueError('Cannot book more than 7 days in advance')
        
        return v

class BookingCreate(BookingBase):
    pass

class BookingResponse(BookingBase):
    id: str
    total_amount: float
    status: BookingStatus
    payment_status: PaymentStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    user: UserResponse
    vehicle: VehicleResponse
    
    class Config:
        from_attributes = True

# Invoice Schemas
class InvoiceBase(BaseModel):
    booking_id: str
    invoice_number: str
    amount: float
    tax_amount: float = 0
    total_amount: float
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        return v
    
    @validator('tax_amount')
    def validate_tax_amount(cls, v):
        if v < 0:
            raise ValueError('Tax amount cannot be negative')
        return v
    
    @validator('total_amount')
    def validate_total_amount(cls, v, values):
        if 'amount' in values and v < values['amount']:
            raise ValueError('Total amount must be greater than or equal to amount')
        return v

class InvoiceCreate(InvoiceBase):
    pass

class InvoiceResponse(InvoiceBase):
    id: str
    issued_date: datetime
    booking: BookingResponse
    
    class Config:
        from_attributes = True

# Availability Query Schema
class AvailabilityQuery(BaseModel):
    pickup_date: date
    return_date: date
    vehicle_type: Optional[VehicleTypeEnum] = None
    vehicle_id: Optional[int] = None
    
    @validator('return_date')
    def validate_dates(cls, v, values):
        if 'pickup_date' in values and v <= values['pickup_date']:
            raise ValueError('Return date must be after pickup date')
        
        if 'pickup_date' in values:
            rental_days = (v - values['pickup_date']).days
            if rental_days > 7:
                raise ValueError('Rental period cannot exceed 7 days')
            
            advance_days = (values['pickup_date'] - date.today()).days
            if advance_days > 7:
                raise ValueError('Cannot book more than 7 days in advance')
        
        return v

# Daily Report Schema
class DailyReportQuery(BaseModel):
    date: date
    vehicle_type: Optional[VehicleTypeEnum] = None

class DailyReportResponse(BaseModel):
    booking_id: str
    pickup_date: date
    return_date: date
    total_amount: float
    status: BookingStatus
    customer_name: str
    customer_email: str
    vehicle_model: str
    license_plate: str
    vehicle_type: str
    capacity: int
    
    class Config:
        from_attributes = True

# Error Response Schema
class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None

# Success Response Schema
class SuccessResponse(BaseModel):
    message: str
    data: Optional[dict] = None