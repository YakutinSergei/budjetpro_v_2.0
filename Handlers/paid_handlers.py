from aiogram import Router, F

from Config_Data.filtrs import PaidFiltersMessage, PaidFiltersCallback
from Handlers.paid_subscription import planned_expenses_handlers

router: Router = Router()
router.message.filter(PaidFiltersMessage())
router.callback_query.filter(PaidFiltersCallback())

router.include_router(planned_expenses_handlers.router)
