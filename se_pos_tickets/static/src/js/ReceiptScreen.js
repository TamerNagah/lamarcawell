odoo.define('se_pos_tickets.ReceiptScreen', function(require) {
    'use strict';

    const { useRef} = owl.hooks;
    const ReceiptScreen = require('point_of_sale.ReceiptScreen');
    const Registries = require('point_of_sale.Registries');

    const SeReceiptScreen = ReceiptScreen =>
        class extends ReceiptScreen {
            /**
             * @override
             */
            constructor() {
                super(...arguments);
                this.giftReceipt = useRef('gift-receipt');
                this.voucherReceipt = useRef('voucher-receipt');
            }
            /**
             * @override
             */
            async printReceipt() {
                $("#order").show();
                $("#voucher").hide();
                $("#gift").hide();
                await super.printReceipt();
            }
            async printVoucher(){
                $("#gift").hide();
                $("#voucher").show();
                $("#order").hide();
                if (this.env.pos.proxy.printer) {
                    const printResult = await this.env.pos.proxy.printer.print_receipt(this.giftReceipt.el.outerHTML);
                    if (printResult.successful) {
                        return true;
                    } else {
                        const { confirmed } = await this.showPopup('ConfirmPopup', {
                            title: printResult.message.title,
                            body: 'Do you want to print using the web printer?',
                        });
                        if (confirmed) {
                            // We want to call the _printWeb when the popup is fully gone
                            // from the screen which happens after the next animation frame.
                            await nextFrame();
                            return await this._printWeb();
                        }
                        return false;
                    }
                } else {
                    return await this._printWeb();                    
                }
            }
            async printGift(){
                $("#voucher").hide();
                $("#order").hide();
                $("#gift").show();
                if (this.env.pos.proxy.printer) {
                    const printResult = await this.env.pos.proxy.printer.print_receipt(this.giftReceipt.el.outerHTML);
                    if (printResult.successful) {
                        return true;
                    } else {
                        const { confirmed } = await this.showPopup('ConfirmPopup', {
                            title: printResult.message.title,
                            body: 'Do you want to print using the web printer?',
                        });
                        if (confirmed) {
                            // We want to call the _printWeb when the popup is fully gone
                            // from the screen which happens after the next animation frame.
                            await nextFrame();
                            return await this._printWeb();
                        }
                        return false;
                    }
                } else {
                    return await this._printWeb();                    
                }
            }
        };

    Registries.Component.extend(ReceiptScreen, SeReceiptScreen);

    return ReceiptScreen;
});
