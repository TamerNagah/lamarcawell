odoo.define('pos_discount_fixed_limit.RemoveLine', function(require) {
    'use strict';
    const PosComponent = require('point_of_sale.PosComponent');
    const DiscountButton = require('pos_discount.DiscountButton');
    const ControlButtonsMixin = require('point_of_sale.ControlButtonsMixin');
    const Registries = require('point_of_sale.Registries');
    const { onChangeOrder, useBarcodeReader } = require('point_of_sale.custom_hooks');
    const { useListener } = require('web.custom_hooks');
    const { useState } = owl.hooks;
    var core = require('web.core');
    var _t = core._t;
    const ProductItem = require('point_of_sale.ProductItem');
    const RemoveLine = (ProductItem) =>
    class extends ProductItem{
    constructor(){
        super(...arguments);
        useListener('click', this.removeLine);

        }
        async removeLine(){
            var order = this.env.pos.get_order();
            var l = order.orderlines.length;
            var orderlines = order.get_orderlines();
            var discount_product = this.env.pos.config.discount_product_id[0];
            if(l>0){
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


    Registries.Component.extend(ProductItem,RemoveLine);
    return RemoveLine;
});