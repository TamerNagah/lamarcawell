odoo.define('pos_discount_fixed_limit.ScreenDisable', function(require) {
    'use strict';
    const PosComponent = require('point_of_sale.PosComponent');
    const DiscountButton = require('pos_discount.DiscountButton');
    const { Component, hooks } = owl;
    const { useExternalListener, useRef, useState } = hooks;
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require('web.custom_hooks');
    const OrderWidget = require('point_of_sale.OrderWidget');
    var core = require('web.core');
    var _t = core._t;
    const ScreenDisable = (OrderWidget) =>
    class extends OrderWidget{
    constructor(){
        super(...arguments);
        useListener('click', this.disable);
        useExternalListener(document, 'keydown', this.keyboardDisable);
        useExternalListener(document, 'keyup', this.keyboardDisable);
        useExternalListener(document, 'keypress', this.keyboardDisable);

        }
        async disable(){
            var order = this.env.pos.get_order();
            var line = order.get_selected_orderline();
            var product = line.product.id;
            var discount_product = this.env.pos.config.discount_product_id[0];
            if (product == discount_product){
                $('.mode-button')
                    .toggleClass('disabled-mode', true)
            	    .prop('disabled', true);
            	$('.input-button')
            	    .toggleClass('disabled-mode', true)
            	    .prop('disabled', true);

            }
            else{
                $('.mode-button')
                    .toggleClass('disabled-mode', false)
            	    .prop('disabled', false);
            	$('.input-button')
            	    .toggleClass('disabled-mode', false)
            	    .prop('disabled', false);
            }
        }
        async keyboardDisable(event){
         var order = this.env.pos.get_order();
         var l = order.orderlines.length
         if(l>0){
           var line = order.get_selected_orderline();
           if(line){
             var product = line.product.id;
             var discount_product = this.env.pos.config.discount_product_id[0];
             if (product == discount_product){
                   event.stopPropagation();
                   event.preventDefault();
                   const { confirmed, payload } = await this.showPopup('ErrorPopup', {
                    title: this.env._t('Cannot modify discount'),
                    body: this.env._t('You cannot modify discount.'),
                    });

                   return false;
             }
           }
         }
        }
    }
    Registries.Component.extend(OrderWidget,ScreenDisable);
    return ScreenDisable;
});