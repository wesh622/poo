package org.junit.jupiter.api;

import java.util.Arrays;
import java.util.Map;
import java.util.HashMap;
import java.lang.reflect.Constructor;
import java.lang.reflect.Method;

import static org.junit.jupiter.api.AssertionUtils.fail;
import static org.junit.jupiter.api.Assertions.assertEquals;


public class ReflectionAssertions {

    public static void assertInstanceOf(Object obj, String expectedClassName) {
        try {
            Class<?> expectedClass = forName(expectedClassName);
            expectedClass.cast(obj);
        } catch (ClassCastException | ClassNotFoundException ex) {
            fail(obj + " is not an instanceof "+expectedClassName);
        }
    }

    public static void assertDeclaredMethod(String className, String methodName, String[] parametersTypesNames, String message) {
        Class<?>[] parametersTypes = Arrays.stream(parametersTypesNames).map(ReflectionAssertions::getClassFromParameterName).toArray(Class<?>[]::new);
        assertDeclaredMethod(className, methodName, parametersTypes, message);
    }

    public static void assertDeclaredMethod(String className, String methodName, Class<?>[] parametersTypes, String message) {
        try {
            Class<?> testedClass = Class.forName(className);
            Method m = testedClass.getMethod(methodName, parametersTypes);
        } catch (ClassNotFoundException cause) {
            fail("Could not found " + className, cause);
        } catch (NoSuchMethodException cause) {
            fail(cause);
        }
    }

    public static void assertDeclaredMethodWithReturnType(String className, String methodName, String[] parametersTypesNames, String returnTypeName, String message) {
        Class<?>[] parametersTypes = Arrays.stream(parametersTypesNames).map(ReflectionAssertions::getClassFromParameterName).toArray(Class<?>[]::new);
        assertDeclaredMethodWithReturnType(className, methodName, parametersTypes, returnTypeName, message);
    }

    public static void assertDeclaredMethodWithReturnType(String className, String methodName, Class<?>[] parametersTypes, String returnTypeName, String message) {
        try {
            assertDeclaredMethodWithReturnType(className, methodName, parametersTypes, ReflectionAssertions.forName(returnTypeName), message);
        } catch (ClassNotFoundException cause) {
            fail("Could not found expected return class " + className, cause);
        } 
    }

    public static void assertDeclaredMethodWithReturnType(String className, String methodName, String[] parametersTypesNames, Class<?> returnTypeName, String message) {
        Class<?>[] parametersTypes = Arrays.stream(parametersTypesNames).map(ReflectionAssertions::getClassFromParameterName).toArray(Class<?>[]::new);
        assertDeclaredMethodWithReturnType(className, methodName, parametersTypes, returnTypeName, message);
    }

    public static void assertDeclaredMethodWithReturnType(String className, String methodName, Class<?>[] parametersTypes, Class<?> returnType, String message) {
        try {
            Class<?> testedClass = Class.forName(className);
            Method m = testedClass.getMethod(methodName, parametersTypes);
            
            Object expected = returnType;
            Object actual = m.getReturnType();

            assertEquals(expected, actual, "wrong return type");
        } catch (ClassNotFoundException cause) {
            fail("Could not found " + className, cause);
        } catch (NoSuchMethodException cause) {
            fail(cause);
        }
    }

    private static Class<?> getClassFromParameterName(String parameterClassName) {
        try {
            return ReflectionAssertions.forName(parameterClassName);
        } catch (ClassNotFoundException cause) {
            fail("Could not found the expected parameter class " + parameterClassName, cause);
        }
        return null;
    }

    public static void assertDeclaredConstructor(String className, String[] parametersTypesNames, String message) {
        Class<?>[] parametersTypes = Arrays.stream(parametersTypesNames).map(ReflectionAssertions::getClassFromParameterName).toArray(Class<?>[]::new);
        assertDeclaredConstructor(className, parametersTypes, message);
    }

    public static void assertDeclaredConstructor(String className, Class<?>[] parametersTypes, String message) {
        try {
            Class<?> testedClass = Class.forName(className);
            Constructor c = testedClass.getConstructor(parametersTypes);
        } catch (ClassNotFoundException cause) {
            fail(cause);
        } catch (NoSuchMethodException cause) {
            fail(cause);
        }
    }

    private static final Map<String, Class<?>> primitiveTypeNameMap = new HashMap<>(8);

    static {
        primitiveTypeNameMap.put("boolean", boolean.class);
        primitiveTypeNameMap.put("byte", byte.class);
        primitiveTypeNameMap.put("char", char.class);
        primitiveTypeNameMap.put("double", double.class);
        primitiveTypeNameMap.put("float", float.class);
        primitiveTypeNameMap.put("int", int.class);
        primitiveTypeNameMap.put("long", long.class);
        primitiveTypeNameMap.put("short", short.class);
        primitiveTypeNameMap.put("void", void.class);
    }

    private static Class<?> resolvePrimitiveClassName(String name) {
        return primitiveTypeNameMap.get(name);
    }
    
    public static Class<?> forName(String name) throws ClassNotFoundException {
        Class<?> primitiveType = resolvePrimitiveClassName(name);
        if (primitiveType != null) {
            return primitiveType;
        }
        return Class.forName(name);
    }

}