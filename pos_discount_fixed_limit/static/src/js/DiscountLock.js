odoo.define('pos_discount_fixed_limit.DiscountLock', function(require) {
    'use strict';
    const PosComponent = require('point_of_sale.PosComponent');
    const DiscountButton = require('pos_discount.DiscountButton');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require('web.custom_hooks');
    const NumpadWidget = require('point_of_sale.NumpadWidget');
    var core = require('web.core');
    var _t = core._t;
    const DiscountLock = (NumpadWidget)=>
     class extends NumpadWidget{
        constructor(){
        super(...arguments);
        useListener('mousedown', this.onClick);
        }
        async onClick(event){
            var order = this.env.pos.get_order();
            var l = order.orderlines.length;
            var orderlines = order.get_orderlines();
            if(l>0){
                var line = order.get_selected_orderline();
                var product = line.product.id;
                var discount_product = this.env.pos.config.discount_product_id[0];
                if (product == discount_product){
                    event.stopPropagation();
                    event.preventDefault();
                    const { confirmed, payload } = this.showPopup('ErrorPopup', {
                    title: this.env._t('Cannot modify discount'),
                    body: this.env._t('You cannot modify discount.'),
                    });
                    if (confirmed) {

                    }
                $('.mode-button')
                    .toggleClass('disabled-mode', true)
            	    .prop('disabled', true);
            	$('.input-button')
            	    .toggleClass('disabled-mode', true)
            	    .prop('disabled', true);
                }
                else{
                    var line;
                    var k;
                    for (var i=0;i<orderlines.length;i++){
                           line= orderlines[i];
                           k = line.product.id;
                           if (k == discount_product){
                              order.remove_orderline(line);
                              break;
                           }
                    }
                }
                }
        }


    }

    Registries.Component.extend(NumpadWidget,DiscountLock);
    return DiscountLock;

});