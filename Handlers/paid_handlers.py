from aiogram import Router, F

from Config_Data.filtrs import PaidFiltersMessage, PaidFiltersCallback
from Handlers.paid_subscription import planned_expenses_handlers, piggy_bank_handlers, report_paid_handlers

router: Router = Router()
router.message.filter(PaidFiltersMessage())
router.callback_query.filter(PaidFiltersCallback())

router.include_router(planned_expenses_handlers.router)
router.include_router(piggy_bank_handlers.router)
router.include_router(report_paid_handlers.router)
