# 🚗 Auto Parts Inventory Management  

## 📖 Project Description  
A web-based inventory management system for auto parts warehouses.  
Features include:  
- **Parts management** (CRUD, stock tracking)  
- **Categories management**  
- **Manufacturers management**  
- **Cars management** (brands, models, years, with images)  
- **Warehouses management** (multi-warehouse support with stock levels)  
- **Orders & Cart system**  
- **PDF invoice generation** for orders  
- **Authentication via JWT + cookies**  
- **Responsive HTML templates** using Jinja2 + Bootstrap  

**Architecture:**  
- **Backend:** FastAPI (async)  
- **Database:** PostgreSQL + SQLAlchemy ORM  
- **Cache:** Redis  
- **Tasks:** Celery  
- **Templates:** Jinja2 (Bootstrap-based)  

---

## ⚙️ Installation & Setup  

### 1. Clone the repository  
```bash
git clone https://github.com/HHamlet/autostock.git
cd autostock
```

### 2. Create a virtual environment  
```bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows
```

### 3. Install dependencies  
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables (`.env`)  
Example:  
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/autostock
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your_secret_key
```

### 5. Run database migrations  
```bash
alembic upgrade head
```

### 6. Start the server  
```bash
uvicorn app.main:app --reload
```

---

## 📂 Core Modules  

### Parts  
- Full CRUD support  
- Linked to categories, manufacturers, and cars  
- `qty_in_stock` automatically recalculated from all warehouses  

### Warehouses  
- Multi-warehouse support  
- Each part tracked per warehouse using `WarehousePartModel`  
- Operations: add, decrease, delete stock  
- Automatic stock recalculation for parts  

### Categories  
- CRUD operations  
- Jinja2 templates (`list.html`, `form.html`)  

### Manufacturers  
- CRUD operations  
- Templates: `list.html`, `form.html`, `detail.html`  

### Cars  
- CRUD operations  
- Support for images (saved and displayed in fixed size)  
- Templates: `form.html`, `list.html`, `detail.html`  

### Orders / Cart  
- Add parts to shopping cart  
- Generate orders  
- Export order to **PDF invoice**  

---

## 📑 Recent Updates  
- ✅ Added **warehouse-part relation** as a full ORM model  
- ✅ Updated `add_part_to_warehouse` to always *add* stock instead of replacing  
- ✅ Implemented stock recalculation (`PartModel.qty_in_stock`) using `func.sum`  
- ✅ Added HTML templates for **categories** (`list.html`)  
- ✅ Built templates for **cars** (`form.html`, `list.html`, `detail.html`) with fixed-size images  
- ✅ Implemented CRUD for **manufacturers** (`form.html`, `list.html`, `detail.html`)  
- ✅ Implemented `print_to_pdf(order_id)` for cart → PDF invoices  
- ✅ Integrated cookie-based authentication & display of current user in templates  

---

## 📌 Roadmap / TODO  
- [ ] Improve UI (tables with filtering & search)  
- [ ] Add Celery tasks (e.g., order notifications)  
- [ ] Build external API for integrations  
- [ ] Write automated tests (pytest + httpx + pytest-asyncio)  

---

## 🛠 Tech Stack  
- **FastAPI** (async backend)  
- **SQLAlchemy + Alembic** (database & migrations)  
- **PostgreSQL** (storage)  
- **Redis** (cache)  
- **Celery** (async tasks)  
- **Jinja2 + Bootstrap** (templates & UI)  

---

## 📜 License  
MIT License. See [LICENSE](LICENSE) for details.  
