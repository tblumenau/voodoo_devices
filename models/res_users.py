<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_users_form_inherit" model="ir.ui.view">
        <field name="name">res.users.preferences.form.inherit</field>
        <field name="model">res.users</field>
        <field name="inherit_id" ref="base.view_users_form_simple_modif"/>
        <field name="arch" type="xml">
           <xpath expr="//field[@name='signature']/ancestor::group[1]" position="after">
                <div class="o_row">
                    <div class="col-6">
                        <label for="voodoo_device_color" class="oe_label"/>
                        <field name="voodoo_device_color"/>
                    </div>
                </div>
                <div class="o_row">
                    <div class="col-6">
                        <label for="voodoo_device_beep" class="oe_label"/>
                        <field name="voodoo_device_beep"/>
                    </div>
                </div>
                <div class="o_row">
                    <div class="col-6">
                        <label for="voodoo_name" class="oe_label"/>
                        <field name="voodoo_name"/>
                    </div>
                </div>
                <div class="o_row">
                    <div class="col-6">
                        <label for="voodoo_seconds" class="oe_label"/>
                        <field name="voodoo_seconds"/>
                    </div>
                </div>
            </xpath>
        </field>
    </record>
</odoo>
